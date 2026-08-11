"""Native Linux Dead Island: Riptide Definitive Edition installation validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .archive import ArchiveInfo, validate_archive
from .errors import ValidationError

NATIVE_EXECUTABLE = "DeadIslandRiptideGame"
DATA0_RELATIVE = Path("DIR") / "Data0.pak"
BASELINE_REQUIRED_ENTRIES = (
    "data/skills/default_levels.xml",
    "data/inventory_gen.scr",
    "data/menu/movies/intromovies.scr",
    "data/scripts/weather/weather.scr",
    "data/scripts/varlist_glow.scd",
    "data/scripts/varlist_glow.scr",
)


@dataclass(frozen=True)
class GameInstallation:
    root: Path
    executable: Path
    data0: Path
    archive: ArchiveInfo


def _is_elf(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return stream.read(4) == b"\x7fELF"
    except OSError:
        return False


def validate_game_root(root: Path) -> GameInstallation:
    root = Path(root).expanduser().resolve()
    executable = root / NATIVE_EXECUTABLE
    data0 = root / DATA0_RELATIVE

    if not executable.is_file():
        raise ValidationError(f"native game executable not found: {executable}")
    if not _is_elf(executable):
        raise ValidationError(f"game executable is not an ELF binary: {executable}")
    if not (root / "DIR").is_dir():
        raise ValidationError(f"game data directory not found: {root / 'DIR'}")

    archive = validate_archive(data0, required_entries=BASELINE_REQUIRED_ENTRIES)
    return GameInstallation(root=root, executable=executable, data0=data0, archive=archive)
