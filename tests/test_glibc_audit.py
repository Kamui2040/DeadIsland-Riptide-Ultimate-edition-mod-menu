import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "packaging" / "appimage" / "audit_glibc.py"
SPEC = importlib.util.spec_from_file_location("dirue_glibc_audit", AUDIT_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def make_dynamic_elf(path: Path, required: str) -> None:
    base = 0x400000
    program_offset = 64
    program_size = 56
    program_count = 2
    dynamic_offset = 0x100
    dynstr_offset = 0x180
    verneed_offset = 0x1C0

    dynstr = b"\0libc.so.6\0" + required.encode("ascii") + b"\0"
    name_offset = dynstr.index(required.encode("ascii"))

    dynamic_entries = (
        (AUDIT.DT_STRTAB, base + dynstr_offset),
        (AUDIT.DT_STRSZ, len(dynstr)),
        (AUDIT.DT_VERNEED, base + verneed_offset),
        (AUDIT.DT_VERNEEDNUM, 1),
        (AUDIT.DT_NULL, 0),
    )
    dynamic_size = 16 * len(dynamic_entries)
    size = 0x300

    data = bytearray(size)
    ident = b"\x7fELF" + bytes((2, 1, 1, 0, 0)) + b"\0" * 7
    data[:16] = ident

    header = struct.pack(
        "<HHIQQQIHHHHHH",
        3,
        62,
        1,
        0,
        program_offset,
        0,
        0,
        64,
        program_size,
        program_count,
        0,
        0,
        0,
    )
    data[16 : 16 + len(header)] = header

    load = struct.pack(
        "<IIQQQQQQ",
        AUDIT.PT_LOAD,
        5,
        0,
        base,
        base,
        size,
        size,
        0x1000,
    )
    dynamic = struct.pack(
        "<IIQQQQQQ",
        AUDIT.PT_DYNAMIC,
        6,
        dynamic_offset,
        base + dynamic_offset,
        base + dynamic_offset,
        dynamic_size,
        dynamic_size,
        8,
    )
    data[program_offset : program_offset + program_size] = load
    data[
        program_offset + program_size : program_offset + 2 * program_size
    ] = dynamic

    for index, entry in enumerate(dynamic_entries):
        start = dynamic_offset + index * 16
        data[start : start + 16] = struct.pack("<qQ", *entry)

    data[dynstr_offset : dynstr_offset + len(dynstr)] = dynstr
    data[verneed_offset : verneed_offset + 16] = struct.pack(
        "<HHIII", 1, 1, 1, 16, 0
    )
    data[verneed_offset + 16 : verneed_offset + 32] = struct.pack(
        "<IHHII", 0, 0, 2, name_offset, 0
    )

    path.write_bytes(data)


def make_static_stripped_elf(path: Path) -> None:
    base = 0x400000
    program_offset = 64
    program_size = 56
    size = 0x180

    data = bytearray(size)
    ident = b"\x7fELF" + bytes((2, 1, 1, 0, 0)) + b"\0" * 7
    data[:16] = ident
    header = struct.pack(
        "<HHIQQQIHHHHHH",
        2,
        62,
        1,
        0,
        program_offset,
        0,
        0,
        64,
        program_size,
        1,
        0,
        0,
        0,
    )
    data[16 : 16 + len(header)] = header
    load = struct.pack(
        "<IIQQQQQQ",
        AUDIT.PT_LOAD,
        5,
        0,
        base,
        base,
        size,
        size,
        0x1000,
    )
    data[program_offset : program_offset + program_size] = load
    path.write_bytes(data)


class GlibcAuditTests(unittest.TestCase):
    def test_reads_required_version_from_stripped_dynamic_elf(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample"
            make_dynamic_elf(path, "GLIBC_2.34")
            self.assertEqual(AUDIT.required_glibc_versions(path), {"GLIBC_2.34"})

    def test_allows_requirement_at_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample"
            make_dynamic_elf(path, "GLIBC_2.34")
            count, maximum, violations = AUDIT.audit([path], "2.34")
            self.assertEqual(count, 1)
            self.assertEqual(maximum, "GLIBC_2.34")
            self.assertEqual(violations, [])

    def test_rejects_requirement_above_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample"
            make_dynamic_elf(path, "GLIBC_2.35")
            _count, maximum, violations = AUDIT.audit([path], "2.34")
            self.assertEqual(maximum, "GLIBC_2.35")
            self.assertEqual(violations, [(path, "GLIBC_2.35")])

    def test_accepts_sectionless_static_elf_without_glibc_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime"
            make_static_stripped_elf(path)
            self.assertEqual(AUDIT.required_glibc_versions(path), set())
            count, maximum, violations = AUDIT.audit([path], "2.34")
            self.assertEqual(count, 1)
            self.assertEqual(maximum, "NONE")
            self.assertEqual(violations, [])

    def test_non_elf_is_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text"
            path.write_text("not an ELF", encoding="utf-8")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.audit([path], "2.34")


if __name__ == "__main__":
    unittest.main()
