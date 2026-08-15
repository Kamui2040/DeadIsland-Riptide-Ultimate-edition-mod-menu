"""Sanitized detail audit for unresolved weather and forced-spawn parity."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
from zipfile import ZipFile

from .archive import validate_archive
from .errors import ValidationError
from .game import validate_game_root
from .preset_audit import PRESET_GROUPS
from .unresolved_audit import (
    FORCED_NATIVE_MEMBER,
    FORCED_PRESET_MEMBER,
    WEATHER_NATIVE_MEMBERS,
    ai_preset_values,
)

_AMBIENT_MEMBER = "scripts/varlist_ambient.scr"
_AMBIENT_NATIVE_MEMBER = "data/scripts/varlist_ambient.scr"
_WEATHER_IDENTITIES = ("f_game_weather", "f_weather_interior")
_AMBIENT_IDENTITIES = ("f_engine_envprobe_factor", "f_lighting_indirect_factor")


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _decode(data: bytes, identity: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode unresolved detail target: {identity}") from exc


def _read_member(archive: ZipFile, member: str, identity: str) -> bytes:
    if member not in archive.namelist():
        raise ValidationError(f"unresolved detail audit missing {identity}: {member}")
    return archive.read(member)


def _named_call_states(text: str, call_name: str, identity: str) -> dict[str, list[str]]:
    pattern = re.compile(
        rf'^(?P<indent>[ \t]*)(?P<comment>//[ \t]*)?'
        rf'{re.escape(call_name)}\(\s*"{re.escape(identity)}"\s*,\s*'
        rf'(?P<value>[^)\r\n]+?)\s*\)\s*[,;]?[ \t]*'
        rf'(?://[^\r\n]*)?\r?$',
        re.MULTILINE,
    )
    active: list[str] = []
    commented: list[str] = []
    for match in pattern.finditer(text):
        value = match.group("value").strip()
        (commented if match.group("comment") else active).append(value)
    return {"active": active, "commented": commented}


def _assignment_states(text: str, name: str) -> dict[str, list[str]]:
    pattern = re.compile(
        rf'^(?P<indent>[ \t]*)(?P<comment>//[ \t]*)?'
        rf'{re.escape(name)}[ \t]*=[ \t]*(?P<value>[^;\r\n]+?)'
        rf'[ \t]*;?[ \t]*(?://[^\r\n]*)?\r?$',
        re.MULTILINE,
    )
    active: list[str] = []
    commented: list[str] = []
    for match in pattern.finditer(text):
        value = match.group("value").strip()
        (commented if match.group("comment") else active).append(value)
    return {"active": active, "commented": commented}


def weather_constant_summary(
    logic_text: str,
    weather_text: str,
    ambient_text: str,
) -> dict[str, object]:
    """Extract only whitelisted released weather/time values and comment state."""
    logic = {
        identity: _named_call_states(logic_text, "set", identity)
        for identity in _WEATHER_IDENTITIES
    }
    weather = {
        "time": _assignment_states(weather_text, "time"),
        "f_game_time": _named_call_states(weather_text, "Set", "f_game_time"),
    }
    ambient = {
        identity: _named_call_states(ambient_text, "VarFloat", identity)
        for identity in _AMBIENT_IDENTITIES
    }

    for scope, identities in (
        ("logic_script", logic),
        ("weather_script", weather),
        ("ambient_script", ambient),
    ):
        for identity, states in identities.items():
            if len(states["active"]) > 1 or len(states["commented"]) > 1:
                raise ValidationError(
                    f"{scope}:{identity}: ambiguous recognized weather value state"
                )

    return {
        "logic_script": logic,
        "weather_script": weather,
        "ambient_script": ambient,
    }


def _quoted_exact_occurrences(data: bytes, value: str) -> int:
    needle = b'"' + value.encode("utf-8") + b'"'
    return data.count(needle)


def global_exact_donor_locations(
    native_members: dict[str, bytes],
    values: tuple[str, ...] | list[str],
) -> dict[str, list[dict[str, object]]]:
    """Locate exact quoted desired strings without emitting the strings themselves."""
    result: dict[str, list[dict[str, object]]] = {}
    for value in values:
        locations: list[dict[str, object]] = []
        for member, data in native_members.items():
            count = _quoted_exact_occurrences(data, value)
            if count:
                locations.append({"member": member, "occurrences": count})
        result[_digest(value)] = locations
    return result


def _preset_info(preset_dir: Path, name: str) -> tuple[Path, str]:
    path = Path(preset_dir) / name
    info = validate_archive(path)
    return path, info.sha256


def audit_unresolved_details(root: Path, preset_dir: Path) -> dict[str, object]:
    """Collect exact safe constants and donor locations without raw spawn lists."""
    game = validate_game_root(root)
    preset_dir = Path(preset_dir)

    with ZipFile(game.data0, "r") as native:
        forced_native_text = _decode(
            _read_member(native, FORCED_NATIVE_MEMBER, "forced-spawn native member"),
            FORCED_NATIVE_MEMBER,
        )
        native_spawn_values = ai_preset_values(forced_native_text)

        native_weather = {
            preset_member: _decode(
                _read_member(native, native_member, f"native {native_member}"),
                native_member,
            )
            for preset_member, native_member in WEATHER_NATIVE_MEMBERS.items()
        }
        native_ambient = _decode(
            _read_member(native, _AMBIENT_NATIVE_MEMBER, "native ambient member"),
            _AMBIENT_NATIVE_MEMBER,
        )
        native_members = {
            info.filename: native.read(info)
            for info in native.infolist()
            if not info.is_dir()
        }

    weather_native_constants = weather_constant_summary(
        native_weather["scripts/logic_script.scr"],
        native_weather["scripts/weather/weather.scr"],
        native_ambient,
    )

    forced: list[dict[str, object]] = []
    for name in PRESET_GROUPS["forced_spawn"][1:]:
        path, preset_sha256 = _preset_info(preset_dir, name)
        with ZipFile(path, "r") as preset:
            preset_text = _decode(
                _read_member(preset, FORCED_PRESET_MEMBER, f"{name} forced-spawn member"),
                f"{name}:{FORCED_PRESET_MEMBER}",
            )
        preset_values = ai_preset_values(preset_text)
        if len(preset_values) != len(native_spawn_values):
            raise ValidationError(
                f"{name}: forced-spawn m_AIPresets count differs from native"
            )
        changed_values = [
            after
            for before, after in zip(native_spawn_values, preset_values)
            if before != after
        ]
        if not changed_values:
            raise ValidationError(f"{name}: expected non-default forced-spawn changes")
        desired_counts = Counter(changed_values)
        locations = global_exact_donor_locations(native_members, list(desired_counts))
        desired = []
        for value, occurrences in sorted(
            desired_counts.items(),
            key=lambda item: _digest(item[0]),
        ):
            digest = _digest(value)
            desired.append(
                {
                    "sha256": digest,
                    "changed_occurrences": occurrences,
                    "native_exact_donors": locations[digest],
                }
            )
        forced.append(
            {
                "preset": name,
                "preset_sha256": preset_sha256,
                "desired_values": desired,
                "all_desired_have_native_exact_donor": all(
                    item["native_exact_donors"] for item in desired
                ),
            }
        )

    weather: list[dict[str, object]] = []
    for name in PRESET_GROUPS["weather_time"][1:]:
        path, preset_sha256 = _preset_info(preset_dir, name)
        with ZipFile(path, "r") as preset:
            logic = _decode(
                _read_member(preset, "scripts/logic_script.scr", f"{name} logic"),
                f"{name}:scripts/logic_script.scr",
            )
            weather_text = _decode(
                _read_member(preset, "scripts/weather/weather.scr", f"{name} weather"),
                f"{name}:scripts/weather/weather.scr",
            )
            ambient = _decode(
                _read_member(preset, _AMBIENT_MEMBER, f"{name} ambient"),
                f"{name}:{_AMBIENT_MEMBER}",
            )
        weather.append(
            {
                "preset": name,
                "preset_sha256": preset_sha256,
                "constants": weather_constant_summary(logic, weather_text, ambient),
            }
        )

    return {
        "archive_sha256": game.archive.sha256,
        "native_weather_constants": weather_native_constants,
        "forced_spawn": forced,
        "weather_time": weather,
    }
