import unittest
from pathlib import Path

from dirue.cli import build_parser


class CliTests(unittest.TestCase):
    def test_native_audit_parser(self):
        args = build_parser().parse_args(["audit-native", "/game"])
        self.assertEqual(args.command, "audit-native")

    def test_preset_audit_defaults_to_repo_preset_dir(self):
        args = build_parser().parse_args(["audit-presets", "/game"])
        self.assertEqual(args.command, "audit-presets")
        self.assertEqual(args.preset_dir, Path("Required_files_and_scripts"))


if __name__ == "__main__":
    unittest.main()
