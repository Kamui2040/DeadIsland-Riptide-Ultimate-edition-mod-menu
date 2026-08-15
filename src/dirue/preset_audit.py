"""Read-only comparison of inherited preset ZIPs against a native Data0."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
from zipfile import ZipFile

from .archive import validate_archive
from .errors import ValidationError
from .game import validate_game_root

PRESET_GROUPS = {
    "ai_difficulty": (
        "ai_norm.zip",
        "ai_Onehit.zip",
        "ai_hard.zip",
        "ai_Headshot.zip",
    ),
    "zombie_size": (
        "PRESETS_XTRASMOL_ZOMSIZE.zip",
        "PRESETS_MIDGET_ZOMSIZE.zip",
        "PRESETS_NORM_ZOMSIZE.zip",
        "PRESETS_LARGE_ZOMSIZE.zip",
        "PRESETS_SUPASIZE_ZOMSIZE.zip",
    ),
    "forced_spawn": (
        "Default_spawns.zip",
        "force_butcher_spawn.zip",
        "Force_ram_spawn.zip",
        "Force_bloater_spawn.zip",
        "Force_thug_spawn.zip",
        "Force_suicide_spawn.zip",
        "Force_bandits_spawn_with_guns.zip",
        "Force_bandits_spawn_with_no_guns.zip",
    ),
    "weather_time": (
        "Time-weather_vanilla.zip",
        "time-weather_Just_night.zip",
        "time-weather_Rain_day.zip",
        "time-weather_Rain_night.zip",
        "time-weather_storm_day.zip",
        "time-weather_storm_night.zip",
        "time-weather_Just_night_darker.zip",
        "time-weather_Rain_night_darker.zip",
        "time-weather_storm_night_darker.zip",
    ),
}


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _target_member(name: str, native_names: set[str]) -> str | None:
    clean = name.lstrip("/")
    candidates = (
        clean,
        f"data/{clean}",
        f"data/presets/{clean}",
        f"data/ai/{clean}",
        f"data/scripts/{clean}",
    )
    matches = list(dict.fromkeys(candidate for candidate in candidates if candidate in native_names))
    if len(matches) > 1:
        raise ValidationError(f"ambiguous native target for preset member {name}")
    return matches[0] if matches else None


def _decode(data: bytes) -> str | None:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def _split_call_arguments(arguments: str) -> tuple[str | None, str]:
    """Return a stable first-argument identity when the common syntax is simple."""
    quoted = re.fullmatch(
        r'\s*"(?P<name>[^"]+)"\s*(?:,\s*(?P<rest>.*))?', arguments
    )
    if quoted:
        return quoted.group("name"), (quoted.group("rest") or "").strip()
    bare = re.fullmatch(
        r'\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*,\s*(?P<rest>.*)', arguments
    )
    if bare:
        return bare.group("name"), bare.group("rest").strip()
    return None, arguments.strip()


def _semantic_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []

    for match in re.finditer(
        r'<prop\b(?=[^>]*\bn="(?P<name>[^"]+)")[^>]*\bv="(?P<value>[^"]+)"[^>]*/>',
        text,
    ):
        pairs.append((f'prop:{match.group("name")}', match.group("value")))

    # Prefix matching is deliberate. Some inherited .pre/.def forms append
    # separators or annotations after a call. The call itself remains the
    # semantic unit, while the remaining structure is checked independently.
    call_pattern = re.compile(
        r'^(?!\s*//)\s*(?P<call>[A-Za-z_][A-Za-z0-9_]*)\s*\('
        r'(?P<arguments>[^\r\n()]*)\)',
        re.MULTILINE,
    )
    generic_ordinals: Counter[str] = Counter()
    for match in call_pattern.finditer(text):
        call_name = match.group("call")
        arguments = match.group("arguments").strip()
        identity, value = _split_call_arguments(arguments)
        if identity is not None:
            key = f"{call_name}:{identity}"
        else:
            generic_ordinals[call_name] += 1
            key = f"{call_name}#{generic_ordinals[call_name]}"
        pairs.append((key, value))

    assignment_pattern = re.compile(
        r'^(?!\s*//)\s*(?:float|int|bool|string)?\s*'
        r'(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[^;\r\n]+)',
        re.MULTILINE,
    )
    for match in assignment_pattern.finditer(text):
        pairs.append((f'assign:{match.group("name")}', match.group("value").strip()))

    return pairs


def _semantic_tokens(text: str) -> dict[str, str]:
    """Extract short semantic values, numbering repeated identities deterministically."""
    pairs = _semantic_pairs(text)
    totals = Counter(key for key, _ in pairs)
    seen: Counter[str] = Counter()
    result: dict[str, str] = {}
    for key, value in pairs:
        seen[key] += 1
        final_key = f"{key}#{seen[key]}" if totals[key] > 1 else key
        result[final_key] = value
    return result


def _semantic_structure(text: str) -> str:
    """Mask recognized values so unrelated text changes remain detectable."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    xml_pattern = re.compile(
        r'(?P<prefix><prop\b(?=[^>]*\bn="[^"]+")[^>]*\bv=")'
        r'[^"]+'
        r'(?P<suffix>"[^>]*/>)'
    )
    normalized = xml_pattern.sub(r"\g<prefix><VALUE>\g<suffix>", normalized)

    quoted_call_pattern = re.compile(
        r'^(?!\s*//)'
        r'(?P<prefix>\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*"[^"]+"\s*,\s*)'
        r'[^\r\n()]*'
        r'(?P<suffix>\)\s*[,;]?(?:\s*//.*)?)$',
        re.MULTILINE,
    )
    normalized = quoted_call_pattern.sub(r"\g<prefix><VALUE>\g<suffix>", normalized)

    generic_call_pattern = re.compile(
        r'^(?!\s*//)'
        r'(?P<prefix>\s*[A-Za-z_][A-Za-z0-9_]*\s*\()'
        r'[^\r\n()]*'
        r'(?P<suffix>\)\s*[,;]?(?:\s*//.*)?)$',
        re.MULTILINE,
    )
    normalized = generic_call_pattern.sub(r"\g<prefix><VALUE>\g<suffix>", normalized)

    assignment_pattern = re.compile(
        r'^(?!\s*//)'
        r'(?P<prefix>\s*(?:float|int|bool|string)?\s*'
        r'[A-Za-z_][A-Za-z0-9_]*\s*=\s*)'
        r'[^;\n]+'
        r'(?P<suffix>\s*;?)',
        re.MULTILINE,
    )
    return assignment_pattern.sub(r"\g<prefix><VALUE>\g<suffix>", normalized)


def _semantic_structure_ignoring_whitespace(text: str) -> str:
    """Normalize indentation, blank lines, and trailing space before masking values."""
    layout_normalized = "\n".join(
        line.strip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
        if line.strip()
    )
    return _semantic_structure(layout_normalized)


def _strip_trailing_active_comment(line: str) -> str:
    """Remove an inline // comment without changing full-line commented code."""
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


def _semantic_structure_ignoring_layout_comments(text: str) -> str:
    """Ignore layout and trailing active comments while preserving comment state."""
    uncommented_layout = "\n".join(
        _strip_trailing_active_comment(line).strip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
        if _strip_trailing_active_comment(line).strip()
    )
    return _semantic_structure(uncommented_layout)


def _raw_layout_structure(text: str) -> str:
    """Normalize layout only; keep every code/comment token and value."""
    return "\n".join(
        line.strip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
        if line.strip()
    )


def _raw_layout_comment_structure(text: str) -> str:
    """Normalize layout and trailing active comments without masking code values."""
    return "\n".join(
        stripped
        for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
        if (stripped := _strip_trailing_active_comment(line).strip())
    )


def _semantic_complete(native_data: bytes, preset_data: bytes) -> bool:
    """Return true only when recognized values explain the complete text difference."""
    native_text = _decode(native_data)
    preset_text = _decode(preset_data)
    if native_text is None or preset_text is None:
        return False
    return _semantic_structure(native_text) == _semantic_structure(preset_text)


def _semantic_complete_ignoring_whitespace(
    native_data: bytes,
    preset_data: bytes,
) -> bool:
    """Return true when recognized values explain the difference apart from layout."""
    native_text = _decode(native_data)
    preset_text = _decode(preset_data)
    if native_text is None or preset_text is None:
        return False
    return (
        _semantic_structure_ignoring_whitespace(native_text)
        == _semantic_structure_ignoring_whitespace(preset_text)
    )


def _semantic_complete_ignoring_layout_comments(
    native_data: bytes,
    preset_data: bytes,
) -> bool:
    """Return true when recognized values explain all but layout/trailing comments."""
    native_text = _decode(native_data)
    preset_text = _decode(preset_data)
    if native_text is None or preset_text is None:
        return False
    return (
        _semantic_structure_ignoring_layout_comments(native_text)
        == _semantic_structure_ignoring_layout_comments(preset_text)
    )


def _layout_only(native_data: bytes, preset_data: bytes) -> bool:
    """Return true only when raw text differs by layout whitespace."""
    native_text = _decode(native_data)
    preset_text = _decode(preset_data)
    if native_text is None or preset_text is None:
        return False
    return _raw_layout_structure(native_text) == _raw_layout_structure(preset_text)


def _layout_or_trailing_comment_only(native_data: bytes, preset_data: bytes) -> bool:
    """Return true only for raw layout and trailing-active-comment differences."""
    native_text = _decode(native_data)
    preset_text = _decode(preset_data)
    if native_text is None or preset_text is None:
        return False
    return (
        _raw_layout_comment_structure(native_text)
        == _raw_layout_comment_structure(preset_text)
    )


def _semantic_delta(native_data: bytes, preset_data: bytes) -> list[dict[str, str]]:
    native_text = _decode(native_data)
    preset_text = _decode(preset_data)
    if native_text is None or preset_text is None:
        return []
    before = _semantic_tokens(native_text)
    after = _semantic_tokens(preset_text)
    changes = []
    for key in sorted(before.keys() & after.keys()):
        if before[key] != after[key]:
            changes.append({"key": key, "native": before[key], "preset": after[key]})
    return changes


def audit_preset_file(preset_path: Path, native_data0: Path) -> dict[str, object]:
    """Compare one validated preset ZIP to native Data0 without extracting either archive."""
    info = validate_archive(preset_path)
    with ZipFile(native_data0, "r") as native, ZipFile(preset_path, "r") as preset:
        native_names = set(native.namelist())
        members = []
        for item in preset.infolist():
            if item.is_dir():
                continue
            target = _target_member(item.filename, native_names)
            preset_data = preset.read(item)
            if target is None:
                members.append(
                    {
                        "preset_member": item.filename,
                        "native_member": None,
                        "status": "missing_native_target",
                        "preset_sha256": _digest(preset_data),
                        "semantic_complete": False,
                        "semantic_complete_ignoring_whitespace": False,
                        "semantic_complete_ignoring_layout_comments": False,
                        "layout_only": False,
                        "layout_or_trailing_comment_only": False,
                    }
                )
                continue
            native_data = native.read(target)
            same = preset_data == native_data
            changes = [] if same else _semantic_delta(native_data, preset_data)
            has_semantic_changes = bool(changes)
            members.append(
                {
                    "preset_member": item.filename,
                    "native_member": target,
                    "status": "same" if same else "different",
                    "preset_sha256": _digest(preset_data),
                    "native_sha256": _digest(native_data),
                    "semantic_changes": changes,
                    "semantic_complete": (
                        True
                        if same
                        else has_semantic_changes
                        and _semantic_complete(native_data, preset_data)
                    ),
                    "semantic_complete_ignoring_whitespace": (
                        True
                        if same
                        else has_semantic_changes
                        and _semantic_complete_ignoring_whitespace(
                            native_data,
                            preset_data,
                        )
                    ),
                    "semantic_complete_ignoring_layout_comments": (
                        True
                        if same
                        else has_semantic_changes
                        and _semantic_complete_ignoring_layout_comments(
                            native_data,
                            preset_data,
                        )
                    ),
                    "layout_only": (
                        True if same else _layout_only(native_data, preset_data)
                    ),
                    "layout_or_trailing_comment_only": (
                        True
                        if same
                        else _layout_or_trailing_comment_only(
                            native_data,
                            preset_data,
                        )
                    ),
                }
            )
    return {
        "name": preset_path.name,
        "size": info.size,
        "sha256": info.sha256,
        "entry_count": info.entry_count,
        "members": members,
    }


def audit_presets(game_root: Path, preset_dir: Path) -> dict[str, object]:
    """Validate the native game and compare all released preset ZIPs read-only."""
    game = validate_game_root(game_root)
    result: dict[str, object] = {}
    for group, names in PRESET_GROUPS.items():
        group_result = []
        for name in names:
            path = preset_dir / name
            if not path.is_file():
                raise ValidationError(f"missing required preset {name}")
            group_result.append(audit_preset_file(path, game.data0))
        result[group] = group_result
    return result
