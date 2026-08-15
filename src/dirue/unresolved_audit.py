"""Read-only sanitized research for unresolved preset-backed parity."""

from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
import re
from zipfile import ZipFile

from .archive import validate_archive
from .errors import ValidationError
from .game import validate_game_root
from .preset_audit import PRESET_GROUPS

HARD_PRESET = "ai_hard.zip"
HARD_PRESET_MEMBER = "ai/zombie/vessel_data_preset_custom_31.scr"
HARD_NATIVE_MEMBER = "data/ai/zombie/vessel_data_preset_custom_31.scr"

FORCED_NATIVE_MEMBER = "data/presets/aispawnbox_pre.def"
FORCED_PRESET_MEMBER = "aispawnbox_pre.def"

WEATHER_PRESET_MEMBERS = (
    "scripts/logic_script.scr",
    "scripts/weather/weather.scr",
)
WEATHER_NATIVE_MEMBERS = {
    member: f"data/{member}" for member in WEATHER_PRESET_MEMBERS
}


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _decode(data: bytes, identity: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode unresolved preset target: {identity}") from exc


def _strip_trailing_active_comment(line: str) -> str:
    if line.lstrip().startswith("//"):
        return line
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
    return line


def _safe_identity(value: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", value):
        return value
    return f"sha256:{_digest(value)}"


def _unknown_shape(line: str) -> str:
    shaped = re.sub(r'"(?:\\.|[^"\\])*"', '"<STRING>"', line)
    shaped = re.sub(
        r"(?<![A-Za-z0-9_])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?![A-Za-z0-9_])",
        "<NUMBER>",
        shaped,
    )
    return shaped


def _structural_line_token(line: str) -> str | None:
    raw = line.strip()
    if not raw:
        return None

    commented = False
    if raw.startswith("//"):
        commented = True
        raw = raw[2:].strip()
        if not raw:
            return "comment"
    else:
        raw = _strip_trailing_active_comment(raw).strip()
        if not raw:
            return None

    prefix = "commented:" if commented else ""

    if raw in {"{", "}", "};", "},"}:
        return f"{prefix}brace:{raw}"

    call = re.match(
        r"^(?P<call>[A-Za-z_][A-Za-z0-9_]*)\s*"
        r"\((?P<arguments>.*)\)\s*[,;]?$",
        raw,
    )
    if call:
        arguments = call.group("arguments").strip()
        quoted = re.match(
            r'^\s*"(?P<identity>[^"]+)"(?:\s*,.*)?$',
            arguments,
        )
        if quoted:
            return (
                f"{prefix}call:{call.group('call')}:"
                f"{_safe_identity(quoted.group('identity'))}"
            )
        return f"{prefix}call:{call.group('call')}"

    assignment = re.match(
        r"^(?:float|int|bool|string)?\s*"
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=",
        raw,
    )
    if assignment:
        return f"{prefix}assign:{assignment.group('name')}"

    first = re.match(r"^(?P<head>[A-Za-z_][A-Za-z0-9_]*)", raw)
    head = first.group("head") if first else "other"
    return f"{prefix}other:{head}:sha256:{_digest(_unknown_shape(raw))}"


def structural_tokens(text: str) -> list[dict[str, object]]:
    """Return sanitized structural identities without argument values."""
    tokens: list[dict[str, object]] = []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for line_number, line in enumerate(normalized.split("\n"), 1):
        token = _structural_line_token(line)
        if token is not None:
            tokens.append({"line_number": line_number, "token": token})
    return tokens


def structural_diff(native_text: str, preset_text: str) -> dict[str, object]:
    """Describe non-value structural changes using sanitized token identities."""
    native = structural_tokens(native_text)
    preset = structural_tokens(preset_text)
    native_sequence = [str(item["token"]) for item in native]
    preset_sequence = [str(item["token"]) for item in preset]

    changes: list[dict[str, object]] = []
    matcher = SequenceMatcher(
        a=native_sequence,
        b=preset_sequence,
        autojunk=False,
    )
    for op, native_start, native_end, preset_start, preset_end in matcher.get_opcodes():
        if op == "equal":
            continue
        changes.append(
            {
                "op": op,
                "native": native[native_start:native_end],
                "preset": preset[preset_start:preset_end],
            }
        )

    return {
        "native_token_count": len(native),
        "preset_token_count": len(preset),
        "structural_change_count": len(changes),
        "changes": changes,
    }


_AI_PRESET_PATTERN = re.compile(
    r'^(?![ \t]*//)[ \t]*SetField\(\s*"m_AIPresets"\s*,\s*'
    r'"(?P<value>[^"\r\n]*)"\s*\)\s*[,;]?[ \t]*'
    r'(?://[^\r\n]*)?\r?$',
    re.MULTILINE,
)


def ai_preset_values(text: str) -> tuple[str, ...]:
    """Return active m_AIPresets values for private donor analysis."""
    return tuple(match.group("value") for match in _AI_PRESET_PATTERN.finditer(text))


def forced_spawn_donor_summary(
    native_text: str,
    preset_text: str,
) -> dict[str, object]:
    """Summarize whether preset target values can be copied from native donors."""
    native = ai_preset_values(native_text)
    preset = ai_preset_values(preset_text)
    if not native:
        raise ValidationError("forced-spawn audit found no native m_AIPresets calls")
    if len(native) != len(preset):
        raise ValidationError(
            "forced-spawn preset m_AIPresets count differs from native"
        )

    changed_ordinals = [
        ordinal
        for ordinal, (before, after) in enumerate(zip(native, preset), 1)
        if before != after
    ]
    desired_counts = Counter(preset[ordinal - 1] for ordinal in changed_ordinals)

    desired_values: list[dict[str, object]] = []
    for value, changed_occurrences in sorted(
        desired_counts.items(),
        key=lambda item: _digest(item[0]),
    ):
        donor_ordinals = [
            ordinal
            for ordinal, native_value in enumerate(native, 1)
            if native_value == value
        ]
        desired_values.append(
            {
                "sha256": _digest(value),
                "changed_occurrences": changed_occurrences,
                "native_donor_ordinals": donor_ordinals,
            }
        )

    return {
        "total_calls": len(native),
        "changed_count": len(changed_ordinals),
        "all_calls_changed": len(changed_ordinals) == len(native),
        "changed_ordinals": changed_ordinals,
        "unique_desired_count": len(desired_values),
        "desired_values": desired_values,
        "all_desired_have_native_donor": all(
            item["native_donor_ordinals"] for item in desired_values
        ),
    }


def _read_member(archive: ZipFile, member: str, identity: str) -> bytes:
    if member not in archive.namelist():
        raise ValidationError(f"unresolved preset audit missing {identity}: {member}")
    return archive.read(member)


def _preset_path(preset_dir: Path, name: str) -> tuple[Path, str]:
    path = Path(preset_dir) / name
    info = validate_archive(path)
    return path, info.sha256


def audit_unresolved_presets(
    root: Path,
    preset_dir: Path,
) -> dict[str, object]:
    """Collect sanitized evidence for hard AI, forced spawn, and weather/time."""
    game = validate_game_root(root)
    preset_dir = Path(preset_dir)

    with ZipFile(game.data0, "r") as native:
        hard_native = _decode(
            _read_member(native, HARD_NATIVE_MEMBER, "hard native member"),
            HARD_NATIVE_MEMBER,
        )
        forced_native = _decode(
            _read_member(native, FORCED_NATIVE_MEMBER, "forced-spawn native member"),
            FORCED_NATIVE_MEMBER,
        )
        weather_native = {
            preset_member: _decode(
                _read_member(
                    native,
                    native_member,
                    f"weather native member {native_member}",
                ),
                native_member,
            )
            for preset_member, native_member in WEATHER_NATIVE_MEMBERS.items()
        }

    hard_path, hard_sha256 = _preset_path(preset_dir, HARD_PRESET)
    with ZipFile(hard_path, "r") as hard_preset:
        hard_text = _decode(
            _read_member(hard_preset, HARD_PRESET_MEMBER, "hard preset member"),
            HARD_PRESET_MEMBER,
        )
    hard = {
        "preset": HARD_PRESET,
        "preset_sha256": hard_sha256,
        "native_member": HARD_NATIVE_MEMBER,
        "preset_member": HARD_PRESET_MEMBER,
        "structure": structural_diff(hard_native, hard_text),
    }

    forced: list[dict[str, object]] = []
    for name in PRESET_GROUPS["forced_spawn"][1:]:
        path, preset_sha256 = _preset_path(preset_dir, name)
        with ZipFile(path, "r") as preset:
            preset_text = _decode(
                _read_member(preset, FORCED_PRESET_MEMBER, f"{name} member"),
                f"{name}:{FORCED_PRESET_MEMBER}",
            )
        forced.append(
            {
                "preset": name,
                "preset_sha256": preset_sha256,
                **forced_spawn_donor_summary(forced_native, preset_text),
            }
        )

    weather: list[dict[str, object]] = []
    for name in PRESET_GROUPS["weather_time"][1:]:
        path, preset_sha256 = _preset_path(preset_dir, name)
        members: dict[str, object] = {}
        with ZipFile(path, "r") as preset:
            for preset_member in WEATHER_PRESET_MEMBERS:
                preset_text = _decode(
                    _read_member(preset, preset_member, f"{name} member"),
                    f"{name}:{preset_member}",
                )
                members[WEATHER_NATIVE_MEMBERS[preset_member]] = {
                    "same_text": preset_text == weather_native[preset_member],
                    "structure": structural_diff(
                        weather_native[preset_member],
                        preset_text,
                    ),
                }
        weather.append(
            {
                "preset": name,
                "preset_sha256": preset_sha256,
                "members": members,
            }
        )

    return {
        "archive_sha256": game.archive.sha256,
        "hard_ai": hard,
        "forced_spawn": forced,
        "weather_time": weather,
    }
