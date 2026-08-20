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


def make_elf(path: Path, required: str) -> None:
    dynstr = b"\0libc.so.6\0" + required.encode("ascii") + b"\0"
    name_offset = dynstr.index(required.encode("ascii"))
    dynstr_offset = 0x100
    verneed_offset = 0x140
    section_offset = 0x200
    section_size = 64
    section_count = 3

    size = section_offset + section_size * section_count
    data = bytearray(size)
    ident = b"\x7fELF" + bytes((2, 1, 1, 0, 0)) + b"\0" * 7
    data[:16] = ident

    header = struct.pack(
        "<HHIQQQIHHHHHH",
        3,
        62,
        1,
        0,
        0,
        section_offset,
        0,
        64,
        0,
        0,
        section_size,
        section_count,
        0,
    )
    data[16 : 16 + len(header)] = header
    data[dynstr_offset : dynstr_offset + len(dynstr)] = dynstr

    verneed = struct.pack("<HHIII", 1, 1, 1, 16, 0)
    vernaux = struct.pack("<IHHII", 0, 0, 2, name_offset, 0)
    data[verneed_offset : verneed_offset + 16] = verneed
    data[verneed_offset + 16 : verneed_offset + 32] = vernaux

    null_section = struct.pack("<IIQQQQIIQQ", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    dynstr_section = struct.pack(
        "<IIQQQQIIQQ",
        0,
        3,
        0,
        0,
        dynstr_offset,
        len(dynstr),
        0,
        0,
        1,
        0,
    )
    verneed_section = struct.pack(
        "<IIQQQQIIQQ",
        0,
        AUDIT.SHT_GNU_VERNEED,
        0,
        0,
        verneed_offset,
        32,
        1,
        1,
        8,
        0,
    )

    for index, section in enumerate((null_section, dynstr_section, verneed_section)):
        start = section_offset + index * section_size
        data[start : start + section_size] = section

    path.write_bytes(data)


class GlibcAuditTests(unittest.TestCase):
    def test_reads_required_version_from_elf_verneed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample"
            make_elf(path, "GLIBC_2.34")
            self.assertEqual(AUDIT.required_glibc_versions(path), {"GLIBC_2.34"})

    def test_allows_requirement_at_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample"
            make_elf(path, "GLIBC_2.34")
            count, maximum, violations = AUDIT.audit([path], "2.34")
            self.assertEqual(count, 1)
            self.assertEqual(maximum, "GLIBC_2.34")
            self.assertEqual(violations, [])

    def test_rejects_requirement_above_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample"
            make_elf(path, "GLIBC_2.35")
            _count, maximum, violations = AUDIT.audit([path], "2.34")
            self.assertEqual(maximum, "GLIBC_2.35")
            self.assertEqual(violations, [(path, "GLIBC_2.35")])

    def test_non_elf_is_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text"
            path.write_text("not an ELF", encoding="utf-8")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.audit([path], "2.34")


if __name__ == "__main__":
    unittest.main()
