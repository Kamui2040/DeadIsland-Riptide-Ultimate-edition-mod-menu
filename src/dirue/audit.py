"""Read-only native Data0 parity audit helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root

DEFAULT_LEVELS = "data/skills/default_levels.xml"
GLOW_SCD = "data/scripts/varlist_glow.scd"
GLOW_SCR = "data/scripts/varlist_glow.scr"
CAR_PHYSICS = "data/odephysics/vehicle/cardi.phx"
OLD_BOAT_PHYSICS = "data/odephysics/vehicle/old_boat_a.phx"
GAME_AUDIO_EFFECTS = "data/gameaudioeffects.scr"
DEFAULT_LOOT = "data/default.loot"
INVENTORY_GEN = "data/inventory_gen.scr"
INVENTORY_SPECIAL = "data/inventory_special.scr"
INTRO_MOVIES = "data/menu/movies/intromovies.scr"

CHARACTER_SKILLS = {
    "logan": "data/skills/logan_skills.xml",
    "purna": "data/skills/purna_skills.xml",
    "samb": "data/skills/samb_skills.xml",
    "xian": "data/skills/xian_skills.xml",
    "john": "data/skills/john_skills.xml",
}

DEFAULT_LEVEL_PROPERTIES = (
    "CameraDefaultFOV",
    "MoveSprintStaminaConsumption",
    "JumpStaminaCost",
    "HideWeaponsDuringSprint",
    "MoveForwardMaxSpeed",
    "MoveBackwardMaxSpeed",
    "MoveStrafeMaxSpeed",
    "MoveAcceleration",
    "MoveDeceleration",
    "MaxAmmoPistol",
    "MaxAmmoRifle",
    "MaxAmmoShotgun",
    "BreakDoorEffectivens",
    "BluntWpnDurabilityLoss",
    "CutWpnDurabilityLoss",
    "RangedWpnDurabilityLoss",
    "BulletWpnDurabilityLoss",
    "BulletPenetrationChance",
)


@dataclass(frozen=True)
class ResearchHint:
    label: str
    member: str
    historical_line: int
    call_name: str


# Historical AHK line numbers are research hints only. They are never patch targets.
FIREARM_RESEARCH_HINTS = (
    ResearchHint("colt_upgrade_1", INVENTORY_GEN, 20596, "ShotTime"),
    ResearchHint("magnum_upgrade_1", INVENTORY_GEN, 20812, "ShotTime"),
    ResearchHint("m9_upgrade_1", INVENTORY_GEN, 21031, "ShotTime"),
    ResearchHint("deag_upgrade_1", INVENTORY_GEN, 21248, "ShotTime"),
    ResearchHint("shorty_upgrade_1", INVENTORY_GEN, 21462, "ShotTime"),
    ResearchHint("shotgun_upgrade_1", INVENTORY_GEN, 21659, "ShotTime"),
    ResearchHint("shotgun_b_upgrade_1", INVENTORY_GEN, 21847, "ShotTime"),
    ResearchHint("shotgun_c_upgrade_1", INVENTORY_GEN, 22035, "ShotTime"),
    ResearchHint("shotgun_d_upgrade_1", INVENTORY_GEN, 22223, "ShotTime"),
    ResearchHint("shotgun_e_upgrade_1", INVENTORY_GEN, 22411, "ShotTime"),
    ResearchHint("shotgun_f_upgrade_1", INVENTORY_GEN, 22599, "ShotTime"),
    ResearchHint("auto_upgrade_1", INVENTORY_GEN, 22791, "ReloadTime"),
    ResearchHint("auto_b_upgrade_1", INVENTORY_GEN, 23000, "ReloadTime"),
    ResearchHint("auto_c_upgrade_1", INVENTORY_GEN, 23209, "ReloadTime"),
    ResearchHint("auto_d_upgrade_1", INVENTORY_GEN, 23418, "ReloadTime"),
    ResearchHint("auto_e_upgrade_1", INVENTORY_GEN, 23627, "ReloadTime"),
    ResearchHint("burst_upgrade_1", INVENTORY_GEN, 23840, "ReloadTime"),
    ResearchHint("burst_b_upgrade_1", INVENTORY_GEN, 24065, "ReloadTime"),
    ResearchHint("single_upgrade_1", INVENTORY_GEN, 24290, "ReloadTime"),
    ResearchHint("single_b_upgrade_1", INVENTORY_GEN, 24515, "ReloadTime"),
    ResearchHint("mccall_upgrade_1", INVENTORY_GEN, 24739, "ShotTime"),
    ResearchHint("fury_revolver", INVENTORY_SPECIAL, 392, "AimFov"),
    ResearchHint("fury_m9", INVENTORY_SPECIAL, 473, "AimFov"),
)


def _decode_member(data: bytes, member: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode required text member {member}") from exc


def _read_text(archive: ZipFile, member: str) -> str:
    try:
        data = archive.read(member)
    except KeyError as exc:
        raise ValidationError(f"missing required audit member {member}") from exc
    return _decode_member(data, member)


def _xml_property_values(text: str, names: tuple[str, ...]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in names:
        pattern = re.compile(
            rf'<prop\b(?=[^>]*\bn="{re.escape(name)}")[^>]*\bv="(?P<value>[^"]+)"[^>]*/>'
        )
        values = [match.group("value") for match in pattern.finditer(text)]
        if len(values) != 1:
            raise ValidationError(
                f"XML property {name}: expected 1 match, found {len(values)}"
            )
        result[name] = values[0]
    return result


def _varfloat_value(text: str, name: str) -> str:
    pattern = re.compile(
        rf'VarFloat\(\s*"{re.escape(name)}"\s*,\s*(?P<value>[^)\s]+)\s*\)'
    )
    values = [match.group("value") for match in pattern.finditer(text)]
    if len(values) != 1:
        raise ValidationError(f"VarFloat {name}: expected 1 match, found {len(values)}")
    return values[0]


def _deeper_pockets_state(text: str) -> dict[str, str]:
    block_pattern = re.compile(
        r'(?P<open><skill\b(?=[^>]*\bid="DeeperPockets")[^>]*>)'
        r'(?P<body>.*?</skill>)',
        re.DOTALL,
    )
    blocks = list(block_pattern.finditer(text))
    if len(blocks) != 1:
        raise ValidationError(
            f"DeeperPockets skill: expected 1 match, found {len(blocks)}"
        )
    block = blocks[0]
    desc = re.search(r'\bdesc_params="(?P<value>[^"]+)"', block.group("open"))
    effects = list(
        re.finditer(
            r'<effect\b(?=[^>]*\bid="InventorySize")[^>]*\bchange="(?P<value>[^"]+)"[^>]*/>',
            block.group("body"),
        )
    )
    if desc is None or len(effects) != 1:
        raise ValidationError("DeeperPockets skill has unexpected structure")
    return {
        "desc_params": desc.group("value"),
        "inventory_change": effects[0].group("value"),
    }


def _active_call_values(text: str, call_name: str) -> Counter[str]:
    pattern = re.compile(
        rf'^(?![ \t]*//)[ \t]*{re.escape(call_name)}\(\s*(?P<value>[^)]+?)\s*\)',
        re.MULTILINE,
    )
    return Counter(match.group("value") for match in pattern.finditer(text))


def _reverb_state(text: str) -> dict[str, object]:
    def line_count(pattern: str) -> int:
        return len(re.findall(pattern, text, re.MULTILINE))

    return {
        "declarations": {
            "preset_active": line_count(r'^\s*!ReverbPreset\('),
            "preset_commented": line_count(r'^\s*!//ReverbPreset\('),
            "mix_active": line_count(r'^\s*!ReverbWetDryMix\('),
            "mix_commented": line_count(r'^\s*!//ReverbWetDryMix\('),
        },
        "calls": {
            "preset_active": line_count(r'^(?!\s*//)\s*ReverbPreset\('),
            "preset_commented": line_count(r'^\s*//\s*ReverbPreset\('),
            "mix_active": line_count(r'^(?!\s*//)\s*ReverbWetDryMix\('),
            "mix_commented": line_count(r'^\s*//\s*ReverbWetDryMix\('),
        },
    }


def _safe_header(header: str) -> str:
    clean = header.split("//", 1)[0].strip()
    call = re.search(r'(?P<kind>[A-Za-z_][A-Za-z0-9_]*)\s*\(\s*"(?P<name>[^"]+)"', clean)
    if call:
        return f'{call.group("kind")}:{call.group("name")}'
    quoted = re.search(r'"(?P<name>[^"]+)"', clean)
    if quoted:
        return quoted.group("name")[:120]
    return clean[:120]


def _brace_paths(lines: list[str]) -> list[tuple[str, ...]]:
    paths: list[tuple[str, ...]] = []
    stack: list[str] = []
    previous = ""
    for line in lines:
        stripped = line.strip()
        code = line.split("//", 1)[0]
        closing = code.count("}")
        for _ in range(min(closing, len(stack))):
            stack.pop()
        paths.append(tuple(stack))
        opening = code.count("{")
        if opening:
            before = code.split("{", 1)[0].strip()
            header = before or previous
            safe = _safe_header(header)
            for _ in range(opening):
                stack.append(safe)
        if stripped and not stripped.startswith("//") and stripped not in {"{", "}"}:
            previous = stripped
    return paths


def _find_hint(text: str, hint: ResearchHint, window: int = 120) -> dict[str, object]:
    lines = text.splitlines()
    paths = _brace_paths(lines)
    target = hint.historical_line - 1
    low = max(0, target - window)
    high = min(len(lines), target + window + 1)
    pattern = re.compile(rf'\b{re.escape(hint.call_name)}\s*\(')
    candidates = [
        index
        for index in range(low, high)
        if not lines[index].lstrip().startswith("//") and pattern.search(lines[index])
    ]
    if not candidates:
        return {"status": "not_found", "historical_line": hint.historical_line}
    index = min(candidates, key=lambda item: abs(item - target))
    return {
        "status": "found",
        "historical_line": hint.historical_line,
        "native_line": index + 1,
        "distance": (index + 1) - hint.historical_line,
        "call": hint.call_name,
        "block_path": list(paths[index]),
    }


def _loot_groups(text: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    paths = _brace_paths(lines)
    groups: dict[tuple[str, ...], dict[str, str]] = {}
    pattern = re.compile(
        r'ColorWeight\(\s*(?P<color>Color_[A-Za-z]+)\s*,\s*(?P<value>[-+0-9.]+)\s*\)'
    )
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if not match:
            continue
        path = paths[index]
        groups.setdefault(path, {})[match.group("color")] = match.group("value")
    result = []
    for path, weights in groups.items():
        if len(weights) >= 5:
            result.append({"block_path": list(path), "weights": dict(sorted(weights.items()))})
    return result


def _statement_ids(text: str) -> list[dict[str, object]]:
    """Return short call/argument identifiers without copying full script lines."""
    pattern = re.compile(
        r'^(?P<indent>[ \t]*)(?P<comment>//[ \t]*)?'
        r'(?P<call>[A-Za-z_][A-Za-z0-9_]*)\s*\(\s*"(?P<arg>[^"]+)"',
        re.MULTILINE,
    )
    return [
        {
            "call": match.group("call"),
            "argument": match.group("arg"),
            "commented": match.group("comment") is not None,
        }
        for match in pattern.finditer(text)
    ]


def audit_data0(path: Path) -> dict[str, object]:
    """Read selected parity facts from a validated Data0 without modifying it."""
    with ZipFile(path, "r") as archive:
        default_levels = _read_text(archive, DEFAULT_LEVELS)
        result: dict[str, object] = {
            "default_levels": _xml_property_values(default_levels, DEFAULT_LEVEL_PROPERTIES),
            "sunflare": {
                "f_pp_glow_factor": _varfloat_value(_read_text(archive, GLOW_SCD), "f_pp_glow_factor"),
                "f_glow_factor": _varfloat_value(_read_text(archive, GLOW_SCR), "f_glow_factor"),
            },
            "deeper_pockets": {
                name: _deeper_pockets_state(_read_text(archive, member))
                for name, member in CHARACTER_SKILLS.items()
            },
            "vehicle_noclip": {
                "car": dict(_active_call_values(_read_text(archive, CAR_PHYSICS), "Ignore")),
                "old_boat": dict(_active_call_values(_read_text(archive, OLD_BOAT_PHYSICS), "Ignore")),
            },
            "reverb": _reverb_state(_read_text(archive, GAME_AUDIO_EFFECTS)),
            "loot_groups": _loot_groups(_read_text(archive, DEFAULT_LOOT)),
            "firearm_research": {},
            "intro": {
                "member_present": INTRO_MOVIES in archive.namelist(),
                "statements": _statement_ids(_read_text(archive, INTRO_MOVIES)),
            },
        }
        cache: dict[str, str] = {}
        research: dict[str, object] = result["firearm_research"]  # type: ignore[assignment]
        for hint in FIREARM_RESEARCH_HINTS:
            if hint.member not in cache:
                cache[hint.member] = _read_text(archive, hint.member)
            research[hint.label] = _find_hint(cache[hint.member], hint)
        return result


def audit_native_game(root: Path) -> dict[str, object]:
    """Validate the native game root, then run a read-only parity audit."""
    game = validate_game_root(root)
    payload = audit_data0(game.data0)
    payload["archive"] = {
        "size": game.archive.size,
        "sha256": game.archive.sha256,
        "entry_count": game.archive.entry_count,
    }
    return payload
