"""Read-only correlation of released firearm line hints to native semantic context."""

from __future__ import annotations

from pathlib import Path
import re
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root
from .research import INVENTORY_GEN, INVENTORY_SPECIAL, _brace_paths, firearm_items

_TARGET_MEMBERS = {
    "INV_GEN": INVENTORY_GEN,
    "INV_spec": INVENTORY_SPECIAL,
}

_SOURCE_SECTIONS = (
    "better_wep_upgrades_yes",
    "betterweppov_62",
    "betterweppov_72",
    "betterweppov_82",
    "swayfix_62",
    "swayfix_72",
    "swayfix_82",
)

_TF_REPLACE = re.compile(
    r'^\s*TF_ReplaceLine\(\s*(?P<target>INV_GEN|INV_spec)\s*,'
    r'\s*"(?P<line>\d+)"\s*,\s*\d+\s*,\s*"(?P<replacement>.*)"\s*\)\s*$',
    re.MULTILINE,
)

_CALL = re.compile(
    r'^(?!\s*//)\s*(?P<call>[A-Za-z_][A-Za-z0-9_]*)'
    r'\(\s*(?P<args>[^)]*?)\s*\)'
)


def _section(text: str, label: str) -> str | None:
    match = re.search(rf'(?m)^{re.escape(label)}:\s*$', text)
    if match is None:
        return None
    next_label = re.search(
        r'(?m)^[A-Za-z_][A-Za-z0-9_]*:\s*$',
        text[match.end() :],
    )
    end = match.end() + next_label.start() if next_label else len(text)
    return text[match.end() : end]


def source_targets(text: str) -> tuple[list[str], list[dict[str, object]]]:
    """Extract active firearm TF_ReplaceLine hints from selected released handlers."""
    sections_found: list[str] = []
    targets: list[dict[str, object]] = []
    for section_name in _SOURCE_SECTIONS:
        section = _section(text, section_name)
        if section is None:
            continue
        sections_found.append(section_name)
        for match in _TF_REPLACE.finditer(section):
            replacement = match.group("replacement")
            replacement_call = _CALL.search(replacement.strip())
            target: dict[str, object] = {
                "section": section_name,
                "source_target": match.group("target"),
                "historical_line": int(match.group("line")),
            }
            if replacement_call is not None:
                target["desired_call"] = replacement_call.group("call")
                target["desired_arguments"] = replacement_call.group("args").strip()[:160]
            targets.append(target)
    return sections_found, targets


def _item_at(paths: list[tuple[str, ...]], line_number: int) -> str | None:
    if line_number < 1 or line_number > len(paths):
        return None
    return next(
        (part for part in reversed(paths[line_number - 1]) if part.startswith("Item:")),
        None,
    )


def _line_identity(lines: list[str], line_number: int) -> dict[str, object]:
    if line_number < 1 or line_number > len(lines):
        return {"kind": "outside_native_file"}
    stripped = lines[line_number - 1].strip()
    if not stripped:
        return {"kind": "blank"}
    if stripped.startswith("//"):
        return {"kind": "comment"}
    if stripped in {"{", "}"}:
        return {"kind": "brace"}
    match = _CALL.search(stripped)
    if match is None:
        return {"kind": "other"}
    return {
        "kind": "call",
        "call": match.group("call"),
        "arguments": match.group("args").strip()[:160],
    }


def _call_context(
    text: str,
) -> tuple[
    list[str],
    list[tuple[str, ...]],
    dict[str, list[dict[str, object]]],
]:
    lines = text.splitlines()
    return lines, _brace_paths(lines), firearm_items(text)


def _nearest(
    item_calls: list[dict[str, object]],
    line_number: int,
    *,
    before: bool,
) -> dict[str, object] | None:
    candidates = [
        entry
        for entry in item_calls
        if (
            entry["line_number"] < line_number
            if before
            else entry["line_number"] > line_number
        )
    ]
    if not candidates:
        return None
    key = max if before else min
    chosen = key(candidates, key=lambda entry: entry["line_number"])
    return {
        "line_number": chosen["line_number"],
        "call": chosen["call"],
        "ordinal_for_call": chosen["ordinal_for_call"],
        "arguments": chosen["arguments"],
    }


def map_targets_to_native(
    targets: list[dict[str, object]],
    native_members: dict[str, str],
) -> list[dict[str, object]]:
    """Attach compact native item/call context to historical source targets."""
    contexts = {
        source_target: _call_context(native_members[source_target])
        for source_target in _TARGET_MEMBERS
    }
    mapped: list[dict[str, object]] = []
    for target in targets:
        source_target = str(target["source_target"])
        line_number = int(target["historical_line"])
        lines, paths, items = contexts[source_target]
        item = _item_at(paths, line_number)
        result = dict(target)
        result["native_member"] = _TARGET_MEMBERS[source_target]
        result["native_item"] = item
        result["native_line"] = _line_identity(lines, line_number)
        item_calls = items.get(item, []) if item is not None else []
        result["previous_relevant_call"] = _nearest(
            item_calls, line_number, before=True
        )
        result["next_relevant_call"] = _nearest(
            item_calls, line_number, before=False
        )
        mapped.append(result)
    return mapped


def _read_archive_text(archive: ZipFile, member: str) -> str:
    try:
        data = archive.read(member)
    except KeyError as exc:
        raise ValidationError(f"missing required source-map member {member}") from exc
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode required source-map member {member}") from exc


def audit_source_map(root: Path, source_file: Path) -> dict[str, object]:
    """Correlate public AHK line hints to native semantic context without writes."""
    game = validate_game_root(root)
    try:
        source_text = Path(source_file).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ValidationError("cannot read released AHK source for mapping") from exc

    sections_found, targets = source_targets(source_text)
    with ZipFile(game.data0, "r") as archive:
        native_members = {
            "INV_GEN": _read_archive_text(archive, INVENTORY_GEN),
            "INV_spec": _read_archive_text(archive, INVENTORY_SPECIAL),
        }
    return {
        "archive_sha256": game.archive.sha256,
        "sections_found": sections_found,
        "missing_sections": [
            name for name in _SOURCE_SECTIONS if name not in sections_found
        ],
        "target_count": len(targets),
        "targets": map_targets_to_native(targets, native_members),
    }
