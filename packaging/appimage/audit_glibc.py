#!/usr/bin/env python3
"""Audit required GLIBC symbol versions in x86-64 AppImage ELF payloads."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import struct
import sys
from typing import Iterable

PT_LOAD = 1
PT_DYNAMIC = 2
DT_NULL = 0
DT_STRTAB = 5
DT_STRSZ = 10
DT_VERNEED = 0x6FFFFFFE
DT_VERNEEDNUM = 0x6FFFFFFF
GLIBC_RE = re.compile(r"^GLIBC_(\d+(?:\.\d+)+)$")


class AuditError(RuntimeError):
    pass


def _version_tuple(text: str) -> tuple[int, ...]:
    match = GLIBC_RE.fullmatch(text)
    if not match:
        raise ValueError(f"invalid GLIBC version: {text}")
    return tuple(int(part) for part in match.group(1).split("."))


def _read_c_string(data: bytes, offset: int) -> str:
    if offset < 0 or offset >= len(data):
        raise AuditError(f"string-table offset out of range: {offset}")
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError("unterminated ELF string-table entry")
    return data[offset:end].decode("ascii", errors="strict")


def _vaddr_to_offset(
    path: Path,
    address: int,
    load_segments: list[tuple[int, int, int]],
) -> int:
    for file_offset, virtual_address, file_size in load_segments:
        if virtual_address <= address < virtual_address + file_size:
            return file_offset + (address - virtual_address)
    raise AuditError(f"ELF virtual address is not file-backed in {path}: 0x{address:x}")


def required_glibc_versions(path: Path) -> set[str]:
    """Return GLIBC versions required by an ELF, including stripped ELFs.

    Runtime dependency information lives in PT_DYNAMIC, not in section headers.
    Reading the dynamic table keeps the audit valid for stripped/static AppImage
    runtimes that legitimately omit their section-header table.
    """

    try:
        data = path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc}") from exc

    if len(data) < 16 or data[:4] != b"\x7fELF":
        return set()

    elf_class = data[4]
    endian = data[5]
    if endian != 1:
        raise AuditError(f"unsupported non-little-endian ELF: {path}")

    if elf_class == 2:
        header_fmt = "<HHIQQQIHHHHHH"
        program_fmt = "<IIQQQQQQ"
        dynamic_fmt = "<qQ"
    elif elf_class == 1:
        header_fmt = "<HHIIIIIHHHHHH"
        program_fmt = "<IIIIIIII"
        dynamic_fmt = "<iI"
    else:
        raise AuditError(f"unsupported ELF class {elf_class}: {path}")

    header_size = struct.calcsize(header_fmt)
    if len(data) < 16 + header_size:
        raise AuditError(f"truncated ELF header: {path}")

    header = struct.unpack_from(header_fmt, data, 16)
    e_phoff = header[4]
    e_phentsize = header[8]
    e_phnum = header[9]

    expected_phentsize = struct.calcsize(program_fmt)
    if e_phoff == 0 or e_phnum == 0:
        raise AuditError(f"ELF has no auditable program-header table: {path}")
    if e_phentsize < expected_phentsize:
        raise AuditError(f"unexpected ELF program-header size: {path}")
    if e_phoff + e_phentsize * e_phnum > len(data):
        raise AuditError(f"ELF program-header table exceeds file bounds: {path}")

    load_segments: list[tuple[int, int, int]] = []
    dynamic_segments: list[tuple[int, int]] = []

    for index in range(e_phnum):
        offset = e_phoff + index * e_phentsize
        program = struct.unpack_from(program_fmt, data, offset)
        p_type = program[0]
        if elf_class == 2:
            p_offset = program[2]
            p_vaddr = program[3]
            p_filesz = program[5]
        else:
            p_offset = program[1]
            p_vaddr = program[2]
            p_filesz = program[4]

        if p_offset + p_filesz > len(data):
            raise AuditError(f"ELF program segment exceeds file bounds: {path}")
        if p_type == PT_LOAD:
            load_segments.append((p_offset, p_vaddr, p_filesz))
        elif p_type == PT_DYNAMIC:
            dynamic_segments.append((p_offset, p_filesz))

    if not load_segments:
        raise AuditError(f"ELF has no file-backed load segment: {path}")

    # A static executable has no PT_DYNAMIC table and therefore cannot carry a
    # glibc dynamic symbol-version requirement. This is the expected shape of
    # the pinned type-2 AppImage runtime, which is statically linked with musl.
    if not dynamic_segments:
        return set()

    if len(dynamic_segments) != 1:
        raise AuditError(f"ELF has ambiguous dynamic segments: {path}")

    dynamic_offset, dynamic_size = dynamic_segments[0]
    dynamic_entry_size = struct.calcsize(dynamic_fmt)
    if dynamic_size % dynamic_entry_size != 0:
        raise AuditError(f"ELF dynamic table has invalid size: {path}")

    dynamic: dict[int, int] = {}
    saw_null = False
    for offset in range(
        dynamic_offset,
        dynamic_offset + dynamic_size,
        dynamic_entry_size,
    ):
        tag, value = struct.unpack_from(dynamic_fmt, data, offset)
        if tag == DT_NULL:
            saw_null = True
            break
        if tag in (DT_STRTAB, DT_STRSZ, DT_VERNEED, DT_VERNEEDNUM):
            if tag in dynamic and dynamic[tag] != value:
                raise AuditError(f"ELF has conflicting dynamic tag {tag}: {path}")
            dynamic[tag] = value

    if not saw_null:
        raise AuditError(f"ELF dynamic table has no terminator: {path}")

    if DT_VERNEED not in dynamic:
        return set()

    if DT_STRTAB not in dynamic or DT_STRSZ not in dynamic:
        raise AuditError(f"ELF version requirements lack a string table: {path}")
    if DT_VERNEEDNUM not in dynamic or dynamic[DT_VERNEEDNUM] <= 0:
        raise AuditError(f"ELF version requirements lack a valid count: {path}")

    string_offset = _vaddr_to_offset(path, dynamic[DT_STRTAB], load_segments)
    string_size = dynamic[DT_STRSZ]
    if string_size <= 0 or string_offset + string_size > len(data):
        raise AuditError(f"ELF dynamic string table exceeds file bounds: {path}")
    strings = data[string_offset : string_offset + string_size]

    cursor = _vaddr_to_offset(path, dynamic[DT_VERNEED], load_segments)
    versions: set[str] = set()
    seen_verneed: set[int] = set()
    expected_verneed = dynamic[DT_VERNEEDNUM]

    for index in range(expected_verneed):
        if cursor in seen_verneed:
            raise AuditError(f"loop in ELF version-needs table: {path}")
        seen_verneed.add(cursor)
        if cursor < 0 or cursor + 16 > len(data):
            raise AuditError(f"truncated ELF version-needs entry: {path}")

        vn_version, vn_cnt, _vn_file, vn_aux, vn_next = struct.unpack_from(
            "<HHIII", data, cursor
        )
        if vn_version != 1:
            raise AuditError(f"unsupported ELF version-needs format: {path}")
        if vn_cnt <= 0:
            raise AuditError(f"ELF version-needs entry has no auxiliaries: {path}")
        if vn_aux == 0:
            raise AuditError(f"ELF version-needs entry lacks auxiliary table: {path}")

        aux = cursor + vn_aux
        seen_aux: set[int] = set()
        for aux_index in range(vn_cnt):
            if aux in seen_aux:
                raise AuditError(f"loop in ELF version-needs aux table: {path}")
            seen_aux.add(aux)
            if aux < 0 or aux + 16 > len(data):
                raise AuditError(f"invalid ELF version-needs aux offset: {path}")

            _hash, _flags, _other, name_offset, next_aux = struct.unpack_from(
                "<IHHII", data, aux
            )
            name = _read_c_string(strings, name_offset)
            if GLIBC_RE.fullmatch(name):
                versions.add(name)

            if aux_index + 1 < vn_cnt:
                if next_aux == 0:
                    raise AuditError(f"truncated ELF version-needs aux chain: {path}")
                aux += next_aux
            elif next_aux != 0:
                # Extra entries beyond vn_cnt make the table internally
                # inconsistent, so fail closed instead of ignoring them.
                raise AuditError(f"ELF version-needs aux count mismatch: {path}")

        if index + 1 < expected_verneed:
            if vn_next == 0:
                raise AuditError(f"truncated ELF version-needs chain: {path}")
            cursor += vn_next
        elif vn_next != 0:
            raise AuditError(f"ELF version-needs count mismatch: {path}")

    return versions


def _iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    seen: set[tuple[int, int]] = set()
    for path in paths:
        if path.is_symlink():
            continue
        if path.is_file():
            stat = path.stat()
            key = (stat.st_dev, stat.st_ino)
            if key not in seen:
                seen.add(key)
                yield path
            continue
        if not path.is_dir():
            raise AuditError(f"audit path does not exist: {path}")
        for root, dirs, files in os.walk(path, followlinks=False):
            root_path = Path(root)
            dirs[:] = [name for name in dirs if not (root_path / name).is_symlink()]
            for name in files:
                candidate = root_path / name
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                stat = candidate.stat()
                key = (stat.st_dev, stat.st_ino)
                if key in seen:
                    continue
                seen.add(key)
                yield candidate


def audit(paths: Iterable[Path], maximum: str) -> tuple[int, str, list[tuple[Path, str]]]:
    allowed = _version_tuple(f"GLIBC_{maximum}")
    elf_count = 0
    maximum_seen: tuple[int, ...] | None = None
    maximum_name = "NONE"
    violations: list[tuple[Path, str]] = []

    for path in _iter_files(paths):
        try:
            with path.open("rb") as handle:
                magic = handle.read(4)
        except OSError as exc:
            raise AuditError(f"cannot inspect {path}: {exc}") from exc
        if magic != b"\x7fELF":
            continue

        elf_count += 1
        for name in required_glibc_versions(path):
            version = _version_tuple(name)
            if maximum_seen is None or version > maximum_seen:
                maximum_seen = version
                maximum_name = name
            if version > allowed:
                violations.append((path, name))

    if elf_count == 0:
        raise AuditError("no ELF files were found in audit inputs")

    violations.sort(key=lambda item: (_version_tuple(item[1]), str(item[0])), reverse=True)
    return elf_count, maximum_name, violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", required=True, dest="maximum")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)

    try:
        _version_tuple(f"GLIBC_{args.maximum}")
        elf_count, maximum_name, violations = audit(args.paths, args.maximum)
    except (AuditError, OSError, UnicodeDecodeError, ValueError) as exc:
        print("GLIBC_AUDIT=FAIL", file=sys.stderr)
        print(f"GLIBC_AUDIT_ERROR={exc}", file=sys.stderr)
        return 2

    if violations:
        print("GLIBC_AUDIT=FAIL", file=sys.stderr)
        for path, version in violations[:10]:
            print(f"GLIBC_AUDIT_VIOLATION={version}:{path}", file=sys.stderr)
        return 3

    print(f"GLIBC_ELF_FILES={elf_count}")
    print(f"GLIBC_MAX_REQUIRED={maximum_name}")
    print("GLIBC_AUDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
