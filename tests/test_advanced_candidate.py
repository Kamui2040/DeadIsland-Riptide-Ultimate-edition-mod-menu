import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from dirue.advanced import CAR_PHYSICS, OLD_BOAT_PHYSICS
from dirue.cli import build_parser
from dirue.engine import build_candidate


class AdvancedCandidateTests(unittest.TestCase):
    def test_cli_accepts_advanced_ready_options(self):
        args = build_parser().parse_args(
            [
                "build-candidate",
                "/source.pak",
                "/candidate.pak",
                "noclip_vehicles",
                "headshot_only_ai",
            ]
        )
        self.assertEqual(args.options, ["noclip_vehicles", "headshot_only_ai"])

    def test_noclip_builds_through_ready_catalog(self):
        text = (
            'ContactParams("Terrain")\n{\n    Ignore(0)\n}\n'
            'ContactParams("SimpleObjects")\n{\n    Ignore(0)\n}\n'
            'ContactParams("NonODEObjects")\n{\n    Ignore(0)\n}\n'
            'ContactParams("ODEObjects")\n{\n    Ignore(0)\n}\n'
            'ContactParams("Water")\n{\n    Ignore(0)\n}\n'
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "Data0.pak"
            candidate = root / "candidate.pak"
            with ZipFile(source, "w") as archive:
                archive.writestr(CAR_PHYSICS, text.replace('ContactParams("Water")\n{\n    Ignore(0)', 'ContactParams("Water")\n{\n    Ignore(1)'))
                archive.writestr(OLD_BOAT_PHYSICS, text)

            source_before = source.read_bytes()
            result = build_candidate(source, candidate, ["noclip_vehicles"])
            self.assertEqual(source.read_bytes(), source_before)
            self.assertEqual(result.changed_members, (CAR_PHYSICS, OLD_BOAT_PHYSICS))
            with ZipFile(candidate, "r") as archive:
                car = archive.read(CAR_PHYSICS).decode("utf-8")
                boat = archive.read(OLD_BOAT_PHYSICS).decode("utf-8")
            self.assertEqual(car.count("Ignore(1)"), 3)
            self.assertEqual(boat.count("Ignore(1)"), 2)


if __name__ == "__main__":
    unittest.main()
