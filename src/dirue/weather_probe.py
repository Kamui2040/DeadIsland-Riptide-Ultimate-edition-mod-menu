"""Private-QA probe for the last weather values and spawn-vector baseline digest.

The returned data is intended for local/private evidence only. It emits only
whitelisted weather/time statement arguments plus a SHA-256 digest of the
native forced-spawn value vector; it never emits the spawn identifier lists.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root
from .preset_audit import PRESET_GROUPS
from .unresolved_audit import (
    FORCED_NATIVE_MEMBER,
    WEATHER_NATIVE_MEMBERS,
    ai_preset_values,
)
from .unresolved_detail import _decode, _preset_info, _read_member


def _strip_trailing_comment(line: str) -> str:
    in_string = False
    escaped = False
    index = 0
    while index + 1 < len(line):
        char = line[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "/" and line[index + 1] == "/":
            return line[:index].rstrip()
        index += 1
    return line.rstrip()


def _split_arguments(arguments: str) -> tuple[str, ...]:
    parts: list[str] = []
    start = 0
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(arguments):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValidationError("weather probe found unbalanced call arguments")
        elif char == "," and depth == 0:
            parts.append(arguments[start:index].strip())
            start = index + 1
    if in_string or depth != 0:
        raise ValidationError("weather probe found malformed call arguments")
    tail = arguments[start:].strip()
    if tail or parts:
        parts.append(tail)
    return tuple(parts)


def _outer_call_arguments(raw: str, call_name: str) -> tuple[str, ...] | None:
    match = re.match(rf"^{re.escape(call_name)}\s*\(", raw)
    if match is None:
        return None
    start = match.end()
    depth = 1
    in_string = False
    escaped = False
    index = start
    while index < len(raw):
        char = raw[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                suffix = raw[index + 1 :].strip()
                if suffix not in {"", ",", ";"}:
                    return None
                return _split_arguments(raw[start:index])
        index += 1
    return None


def _unquote(value: str) -> str | None:
    if len(value) < 2 or value[0] != '"' or value[-1] != '"':
        return None
    body = value[1:-1]
    if '"' in body:
        return None
    return body


def _prepare_line(line: str) -> tuple[bool, str]:
    raw = line.strip()
    if not raw:
        return False, ""
    is_commented = raw.startswith("//")
    if is_commented:
        raw = raw[2:].strip()
    return is_commented, _strip_trailing_comment(raw).strip()


def _call_argument_states(text: str, call_name: str, identity: str) -> dict[str, list[list[str]]]:
    active: list[list[str]] = []
    commented: list[list[str]] = []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for line in normalized.split("\n"):
        is_commented, raw = _prepare_line(line)
        if not raw:
            continue
        arguments = _outer_call_arguments(raw, call_name)
        if not arguments or _unquote(arguments[0]) != identity:
            continue
        target = commented if is_commented else active
        target.append(list(arguments[1:]))
    if len(active) > 1 or len(commented) > 1:
        raise ValidationError(f"weather probe found ambiguous {call_name}:{identity} state")
    return {"active": active, "commented": commented}


def _assignment_states(text: str, name: str) -> dict[str, list[str]]:
    active: list[str] = []
    commented: list[str] = []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    pattern = re.compile(rf"^(?:float\s+)?{re.escape(name)}\s*=\s*(?P<value>.+?)\s*;?$")
    for line in normalized.split("\n"):
        is_commented, raw = _prepare_line(line)
        if not raw:
            continue
        match = pattern.match(raw)
        if match is None:
            continue
        value = match.group("value").strip()
        if value.endswith(";"):
            value = value[:-1].rstrip()
        (commented if is_commented else active).append(value)
    if len(active) > 1 or len(commented) > 1:
        raise ValidationError(f"weather probe found ambiguous assignment:{name} state")
    return {"active": active, "commented": commented}


def statement_summary(logic_text: str, weather_text: str) -> dict[str, object]:
    """Return only the four whitelisted released weather/time statement values."""
    return {
        "logic_script": {
            "f_game_weather": _call_argument_states(logic_text, "set", "f_game_weather"),
            "f_weather_interior": _call_argument_states(logic_text, "set", "f_weather_interior"),
        },
        "weather_script": {
            "time": _assignment_states(weather_text, "time"),
            "f_game_time": _call_argument_states(weather_text, "Set", "f_game_time"),
        },
    }


def _spawn_vector_digest(values: tuple[str, ...]) -> str:
    canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def audit_weather_probe(root: Path, preset_dir: Path) -> dict[str, object]:
    game = validate_game_root(root)
    preset_dir = Path(preset_dir)

    with ZipFile(game.data0, "r") as native:
        forced_text = _decode(
            _read_member(native, FORCED_NATIVE_MEMBER, "forced-spawn native member"),
            FORCED_NATIVE_MEMBER,
        )
        spawn_values = ai_preset_values(forced_text)
        if len(spawn_values) != 165:
            raise ValidationError(
                f"weather probe expected 165 native m_AIPresets calls, found {len(spawn_values)}"
            )
        native_weather = {
            preset_member: _decode(
                _read_member(native, native_member, f"native {native_member}"),
                native_member,
            )
            for preset_member, native_member in WEATHER_NATIVE_MEMBERS.items()
        }

    native_statements = statement_summary(
        native_weather["scripts/logic_script.scr"],
        native_weather["scripts/weather/weather.scr"],
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
        weather.append(
            {
                "preset": name,
                "preset_sha256": preset_sha256,
                "statements": statement_summary(logic, weather_text),
            }
        )

    return {
        "archive_sha256": game.archive.sha256,
        "forced_spawn_native_call_count": len(spawn_values),
        "forced_spawn_native_vector_sha256": _spawn_vector_digest(spawn_values),
        "native_weather_statements": native_statements,
        "weather_time": weather,
    }
