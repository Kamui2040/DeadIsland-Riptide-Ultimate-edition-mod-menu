"""Sanitized same-member token research for unresolved forced-spawn modes."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from .archive import validate_archive
from .errors import ValidationError
from .game import validate_game_root
from .spawn_recipe_audit import _is_token, _parts
from .unresolved_audit import (
    FORCED_NATIVE_MEMBER,
    FORCED_PRESET_MEMBER,
    ai_preset_values,
)


_UNRESOLVED_PRESETS = (
    "force_butcher_spawn.zip",
    "Force_ram_spawn.zip",
    "Force_bloater_spawn.zip",
    "Force_thug_spawn.zip",
)
_QUOTED_PATTERN = re.compile(r'"(?P<value>(?:\\.|[^"\\])*)"')


def _digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _vector_digest(values: tuple[str, ...]) -> str:
    canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _decode(data: bytes, identity: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(
            f"cannot decode same-member spawn audit target: {identity}"
        ) from exc


def _read_member(archive: ZipFile, member: str, identity: str) -> bytes:
    if member not in archive.namelist():
        raise ValidationError(
            f"same-member spawn audit missing {identity}: {member}"
        )
    return archive.read(member)


def quoted_values(text: str) -> tuple[str, ...]:
    """Return raw quoted-string contents from one native member."""
    return tuple(match.group("value") for match in _QUOTED_PATTERN.finditer(text))


@dataclass(frozen=True)
class _QuotedTokenSource:
    value_sha256: str
    part_index: int


def _quoted_token_sources(values: tuple[str, ...]) -> dict[str, _QuotedTokenSource]:
    choices: dict[str, list[_QuotedTokenSource]] = {}
    for value in values:
        value_digest = _digest_text(value)
        for part_index, part in enumerate(_parts(value)):
            if not _is_token(part):
                continue
            choices.setdefault(part, []).append(
                _QuotedTokenSource(
                    value_sha256=value_digest,
                    part_index=part_index,
                )
            )

    sources: dict[str, _QuotedTokenSource] = {}
    for token, token_choices in choices.items():
        sources[token] = min(
            token_choices,
            key=lambda source: (source.value_sha256, source.part_index),
        )
    return sources


def _candidate_recipe(
    native_spawn_values: tuple[str, ...],
    target: str,
    base_ordinal: int,
    token_sources: dict[str, _QuotedTokenSource],
) -> dict[str, object] | None:
    base = native_spawn_values[base_ordinal - 1]
    base_parts = _parts(base)
    target_parts = _parts(target)
    if len(base_parts) != len(target_parts):
        return None

    reconstructed = list(base_parts)
    replacements: list[dict[str, object]] = []
    for part_index, (before, after) in enumerate(zip(base_parts, target_parts)):
        if before == after:
            continue
        if not _is_token(before) or not _is_token(after):
            return None
        source = token_sources.get(after)
        if source is None:
            return None
        replacements.append(
            {
                "part_index": part_index,
                "donor_value_sha256": source.value_sha256,
                "donor_part_index": source.part_index,
                "token_length": len(after),
            }
        )
        reconstructed[part_index] = after

    if not replacements:
        return None
    rebuilt = "".join(reconstructed)
    if rebuilt != target:
        raise ValidationError("same-member spawn reconstruction did not match target")

    return {
        "base_ordinal": base_ordinal,
        "base_value_sha256": _digest_text(base),
        "part_count": len(base_parts),
        "replacement_count": len(replacements),
        "replacements": replacements,
        "reconstructed_sha256": _digest_text(rebuilt),
    }


def same_member_recipe_summary(
    native_text: str,
    native_spawn_values: tuple[str, ...],
    target: str,
) -> dict[str, object]:
    """Find a whole-token recipe using any quoted string in the same member."""
    if len(native_spawn_values) != 165:
        raise ValidationError("same-member spawn audit requires 165 native spawn values")

    native_quoted = quoted_values(native_text)
    if not native_quoted:
        raise ValidationError("same-member spawn audit found no quoted strings")
    if target in native_quoted:
        raise ValidationError(
            "same-member spawn audit target already exists as an exact quoted donor"
        )

    token_sources = _quoted_token_sources(native_quoted)
    candidates: list[dict[str, object]] = []
    for base_ordinal in range(1, len(native_spawn_values) + 1):
        candidate = _candidate_recipe(
            native_spawn_values,
            target,
            base_ordinal,
            token_sources,
        )
        if candidate is not None:
            candidates.append(candidate)

    if not candidates:
        return {
            "target_sha256": _digest_text(target),
            "target_length": len(target),
            "recipe_found": False,
            "recipe": None,
        }

    candidates.sort(
        key=lambda item: (
            int(item["replacement_count"]),
            int(item["base_ordinal"]),
            tuple(
                (
                    int(change["part_index"]),
                    str(change["donor_value_sha256"]),
                    int(change["donor_part_index"]),
                )
                for change in item["replacements"]  # type: ignore[union-attr]
            ),
        )
    )
    return {
        "target_sha256": _digest_text(target),
        "target_length": len(target),
        "recipe_found": True,
        "recipe": candidates[0],
    }


def unresolved_member_mode_summary(
    native_text: str,
    native_values: tuple[str, ...],
    preset_values: tuple[str, ...],
) -> dict[str, object]:
    if len(native_values) != 165 or len(preset_values) != 165:
        raise ValidationError("same-member spawn audit requires exactly 165 values")

    changed_ordinals = tuple(
        ordinal
        for ordinal, (before, after) in enumerate(zip(native_values, preset_values), 1)
        if before != after
    )
    preserved_ordinals = tuple(
        ordinal
        for ordinal, (before, after) in enumerate(zip(native_values, preset_values), 1)
        if before == after
    )
    desired = Counter(preset_values[ordinal - 1] for ordinal in changed_ordinals)
    if len(desired) != 1:
        raise ValidationError(
            "same-member spawn audit expected one repeated desired identifier"
        )
    target, changed_occurrences = next(iter(desired.items()))
    return {
        "changed_count": len(changed_ordinals),
        "changed_occurrences": changed_occurrences,
        "preserved_ordinals": list(preserved_ordinals),
        **same_member_recipe_summary(native_text, native_values, target),
    }


def audit_same_member_spawn_recipes(
    root: Path,
    preset_dir: Path,
) -> dict[str, object]:
    """Audit same-member quoted-token recipes for the four remaining modes."""
    game = validate_game_root(root)
    preset_dir = Path(preset_dir)

    with ZipFile(game.data0, "r") as archive:
        native_bytes = _read_member(
            archive,
            FORCED_NATIVE_MEMBER,
            "native forced-spawn member",
        )
    native_text = _decode(native_bytes, FORCED_NATIVE_MEMBER)
    native_values = ai_preset_values(native_text)
    if len(native_values) != 165:
        raise ValidationError(
            f"same-member spawn audit expected 165 native values, found {len(native_values)}"
        )

    modes: list[dict[str, object]] = []
    for preset_name in _UNRESOLVED_PRESETS:
        path = preset_dir / preset_name
        preset_info = validate_archive(path)
        with ZipFile(path, "r") as archive:
            preset_text = _decode(
                _read_member(
                    archive,
                    FORCED_PRESET_MEMBER,
                    f"{preset_name} member",
                ),
                f"{preset_name}:{FORCED_PRESET_MEMBER}",
            )
        preset_values = ai_preset_values(preset_text)
        modes.append(
            {
                "preset": preset_name,
                "preset_sha256": preset_info.sha256,
                **unresolved_member_mode_summary(
                    native_text,
                    native_values,
                    preset_values,
                ),
            }
        )

    return {
        "archive_sha256": game.archive.sha256,
        "native_member_sha256": sha256(native_bytes).hexdigest(),
        "native_vector_sha256": _vector_digest(native_values),
        "native_call_count": len(native_values),
        "native_quoted_string_count": len(quoted_values(native_text)),
        "modes": modes,
    }
