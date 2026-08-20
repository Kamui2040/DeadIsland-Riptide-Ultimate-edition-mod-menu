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

SHT_GNU_VERNEED = 0x6FFFFFFE
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


def required_glibc_versions(path: Path) -> set[str]:
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
        section_fmt = "<IIQQQQIIQQ"
    elif elf_class == 1:
        header_fmt = "<HHIIIIIHHHHHH"
        section_fmt = "<IIIIIIIIII"
    else:
        raise AuditError(f"unsupported ELF class {elf_class}: {path}")

    header_size = struct.calcsize(header_fmt)
    if len(data) < 16 + header_size:
        raise AuditError(f"truncated ELF header: {path}")

    header = struct.unpack_from(header_fmt, data, 16)
    if elf_class == 2:
        e_shoff = header[5]
        e_shentsize = header[10]
        e_shnum = header[11]
    else:
        e_shoff = header[5]
        e_shentsize = header[10]
        e_shnum = header[11]

    expected_shentsize = struct.calcsize(section_fmt)
    if e_shoff == 0 or e_shnum == 0:
        raise AuditError(f"ELF has no auditable section table: {path}")
    if e_shentsize < expected_shentsize:
        raise AuditError(f"unexpected ELF section-header size: {path}")
    if e_shoff + e_shentsize * e_shnum > len(data):
        raise AuditError(f"ELF section table exceeds file bounds: {path}")

    sections: list[tuple[int, ...]] = []
    for index in range(e_shnum):
        offset = e_shoff + index * e_shentsize
        sections.append(struct.unpack_from(section_fmt, data, offset))

    versions: set[str] = set()
    for section in sections:
        sh_type = section[1]
        if sh_type != SHT_GNU_VERNEED:
            continue

        sh_offset = section[4]
        sh_size = section[5]
        sh_link = section[6]
        if sh_link >= len(sections):
            raise AuditError(f"invalid GLIBC version string-table link: {path}")
        if sh_offset + sh_size > len(data):
            raise AuditError(f"GLIBC version section exceeds file bounds: {path}")

        string_section = sections[sh_link]
        str_offset = string_section[4]
        str_size = string_section[5]
        if str_offset + str_size > len(data):
            raise AuditError(f"ELF dynamic string table exceeds file bounds: {path}")
        strings = data[str_offset : str_offset + str_size]

        cursor = sh_offset
        section_end = sh_offset + sh_size
        seen_verneed: set[int] = set()
        while cursor < section_end:
            if cursor in seen_verneed:
                raise AuditError(f"loop in ELF version-needs table: {path}")
            seen_verneed.add(cursor)
            if cursor + 16 > section_end:
                raise AuditError(f"truncated ELF version-needs entry: {path}")

            vn_version, vn_cnt, _vn_file, vn_aux, vn_next = struct.unpack_from(
                "<HHIII", data, cursor
            )
            if vn_version != 1:
                raise AuditError(f"unsupported ELF version-needs format: {path}")

            aux = cursor + vn_aux
            seen_aux: set[int] = set()
            for _ in range(vn_cnt):
                if aux in seen_aux:
                    raise AuditError(f"loop in ELF version-needs aux table: {path}")
                seen_aux.add(aux)
                if aux < sh_offset or aux + 16 > section_end:
                    raise AuditError(f"invalid ELF version-needs aux offset: {path}")

                _hash, _flags, _other, name_offset, next_aux = struct.unpack_from(
                    "<IHHII", data, aux
                )
                name = _read_c_string(strings, name_offset)
                if GLIBC_RE.fullmatch(name):
                    versions.add(name)

                if next_aux == 0:
                    break
                aux += next_aux

            if vn_next == 0:
                break
            cursor += vn_next

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
    except (AuditError, OSError, ValueError) as exc:
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
