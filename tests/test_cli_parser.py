import unittest
from pathlib import Path

from dirue.cli import build_parser


class CliParserTests(unittest.TestCase):
    def test_audit_native_parser(self):
        args = build_parser().parse_args(["audit-native", "/game"])
        self.assertEqual(args.command, "audit-native")
        self.assertEqual(args.root, Path("/game"))

    def test_audit_research_parser(self):
        args = build_parser().parse_args(["audit-research", "/game"])
        self.assertEqual(args.command, "audit-research")
        self.assertEqual(args.root, Path("/game"))


if __name__ == "__main__":
    unittest.main()
