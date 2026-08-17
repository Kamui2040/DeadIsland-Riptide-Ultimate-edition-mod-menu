import os
from pathlib import Path
import subprocess
import sys
import unittest

from dirue.cli import build_parser


class CliTests(unittest.TestCase):
    def test_native_audit_parser(self):
        args = build_parser().parse_args(["audit-native", "/game"])
        self.assertEqual(args.command, "audit-native")

    def test_preset_audit_defaults_to_repo_preset_dir(self):
        args = build_parser().parse_args(["audit-presets", "/game"])
        self.assertEqual(args.command, "audit-presets")
        self.assertEqual(args.preset_dir, Path("Required_files_and_scripts"))

    def test_module_invocation_executes_cli(self):
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, "-m", "dirue.cli", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: dirue", result.stdout)
        self.assertIn("build-candidate", result.stdout)


if __name__ == "__main__":
    unittest.main()
