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

    def test_audit_fov_recoil_parser(self):
        args = build_parser().parse_args(["audit-fov-recoil", "/game"])
        self.assertEqual(args.command, "audit-fov-recoil")
        self.assertEqual(args.root, Path("/game"))

    def test_build_candidate_parser(self):
        args = build_parser().parse_args(
            [
                "build-candidate",
                "/source.pak",
                "/candidate.pak",
                "reduce_sprint_stamina",
            ]
        )
        self.assertEqual(args.command, "build-candidate")
        self.assertEqual(args.source, Path("/source.pak"))
        self.assertEqual(args.destination, Path("/candidate.pak"))
        self.assertEqual(args.options, ["reduce_sprint_stamina"])


if __name__ == "__main__":
    unittest.main()
