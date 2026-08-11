from pathlib import Path
import tempfile
import unittest
import zipfile

from dirue.errors import ValidationError
from dirue.game import BASELINE_REQUIRED_ENTRIES, validate_game_root


class GameValidationTests(unittest.TestCase):
    def make_game(self, root: Path, elf: bool = True) -> None:
        executable = root / "DeadIslandRiptideGame"
        executable.write_bytes((b"\x7fELF" if elf else b"MZ00") + b"fake")
        data_dir = root / "DIR"
        data_dir.mkdir()
        with zipfile.ZipFile(data_dir / "Data0.pak", "w") as archive:
            for name in BASELINE_REQUIRED_ENTRIES:
                archive.writestr(name, b"fixture")

    def test_valid_native_layout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_game(root)
            game = validate_game_root(root)
            self.assertEqual(game.archive.entry_count, len(BASELINE_REQUIRED_ENTRIES))

    def test_rejects_non_elf_executable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_game(root, elf=False)
            with self.assertRaises(ValidationError):
                validate_game_root(root)


if __name__ == "__main__":
    unittest.main()
