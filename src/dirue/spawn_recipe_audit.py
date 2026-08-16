"""Sanitized read-only reconstruction audit for unresolved forced-spawn identifiers."""

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
from .preset_audit import PRESET_GROUPS
from .unresolved_audit import (
    FORCED_NATIVE_MEMBER,
    FORCED_PRESET_MEMBER,
    ai_preset_values,
)


_UNRESOLVED_PRESETS = tuple(PRESET_GROUPS["forced_spawn"][1:5]) + (
    PRESET_GROUPS["forced_spawn"][7],
)
_PART_PATTERN = re.compile(r"[A-Za-z0-9]+|[^A-Za-z0-9]+")


def _digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _vector_digest(values: tuple[str, ...]) -> str:
    canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _decode(data: bytes, identity: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode spawn recipe audit target: {identity}") from exc


def _read_member(archive: ZipFile, member: str, identity: str) -> bytes:
    if member not in archive.namelist():
        raise ValidationError(f"spawn recipe audit missing {identity}: {member}")
    return archive.read(member)


def _parts(value: str) -> tuple[str, ...]:
    parts = tuple(_PART_PATTERN.findall(value))
    if "".join(parts) != value:
        raise ValidationError("spawn recipe tokenizer did not round-trip identifier")
    return parts


def _is_token(part: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9]+", part) is not None


@dataclass(frozen=True)
class _TokenSource:
    ordinal: int
    part_index: int
    value_sha256: str


def _token_sources(native_values: tuple[str, ...]) -> dict[str, _TokenSource]:
    sources: dict[str, _TokenSource] = {}
    for ordinal, value in enumerate(native_values, 1):
        value_digest = _digest_text(value)
        for part_index, part in enumerate(_parts(value)):
            if not _is_token(part):
                continue
            sources.setdefault(
                part,
                _TokenSource(
                    ordinal=ordinal,
                    part_index=part_index,
                    value_sha256=value_digest,
                ),
            )
    return sources


def _candidate_recipe(
    native_values: tuple[str, ...],
    target: str,
    base_ordinal: int,
    token_sources: dict[str, _TokenSource],
) -> dict[str, object] | None:
    base = native_values[base_ordinal - 1]
    base_parts = _parts(base)
    target_parts = _parts(target)
    if len(base_parts) != len(target_parts):
        return None

    replacements: list[dict[str, object]] = []
    reconstructed = list(base_parts)
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
                "donor_ordinal": source.ordinal,
                "donor_part_index": source.part_index,
                "donor_value_sha256": source.value_sha256,
                "token_length": len(after),
            }
        )
        reconstructed[part_index] = after

    if not replacements:
        return None
    rebuilt = "".join(reconstructed)
    if rebuilt != target:
        raise ValidationError("spawn recipe reconstruction did not match target")

    return {
        "base_ordinal": base_ordinal,
        "base_value_sha256": _digest_text(base),
        "part_count": len(base_parts),
        "replacement_count": len(replacements),
        "replacements": replacements,
        "reconstructed_sha256": _digest_text(rebuilt),
    }


def token_recipe_summary(
    native_values: tuple[str, ...],
    target: str,
) -> dict[str, object]:
    """Find the shortest whole-token recipe using only pristine native values."""
    if not native_values:
        raise ValidationError("spawn recipe audit received no native values")
    if target in native_values:
        raise ValidationError("spawn recipe audit target already has an exact native donor")

    sources = _token_sources(native_values)
    candidates: list[dict[str, object]] = []
    for base_ordinal in range(1, len(native_values) + 1):
        candidate = _candidate_recipe(
            native_values,
            target,
            base_ordinal,
            sources,
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
                    int(change["donor_ordinal"]),
                    int(change["donor_part_index"]),
                )
                for change in item["replacements"]  # type: ignore[union-attr]
            ),
        )
    )
    best = candidates[0]
    return {
        "target_sha256": _digest_text(target),
        "target_length": len(target),
        "recipe_found": True,
        "recipe": best,
    }


def unresolved_mode_summary(
    native_values: tuple[str, ...],
    preset_values: tuple[str, ...],
) -> dict[str, object]:
    if len(native_values) != 165 or len(preset_values) != 165:
        raise ValidationError("spawn recipe audit requires exactly 165 values")

    changed_ordinals = tuple(
        ordinal
        for ordinal, (before, after) in enumerate(zip(native_values, preset_values), 1)
        if before != after
    )
    desired = Counter(preset_values[ordinal - 1] for ordinal in changed_ordinals)
    if len(desired) != 1:
        raise ValidationError(
            "spawn recipe audit expected one repeated desired identifier per unresolved mode"
        )
    target, changed_occurrences = next(iter(desired.items()))
    recipe = token_recipe_summary(native_values, target)
    return {
        "changed_count": len(changed_ordinals),
        "changed_occurrences": changed_occurrences,
        **recipe,
    }


def audit_spawn_recipes(root: Path, preset_dir: Path) -> dict[str, object]:
    """Audit public-safe whole-token reconstruction recipes for unresolved modes."""
    game = validate_game_root(root)
    preset_dir = Path(preset_dir)

    with ZipFile(game.data0, "r") as archive:
        native_text = _decode(
            _read_member(archive, FORCED_NATIVE_MEMBER, "native forced-spawn member"),
            FORCED_NATIVE_MEMBER,
        )
    native_values = ai_preset_values(native_text)
    if len(native_values) != 165:
        raise ValidationError(
            f"spawn recipe audit expected 165 native values, found {len(native_values)}"
        )

    modes: list[dict[str, object]] = []
    for preset_name in _UNRESOLVED_PRESETS:
        path = preset_dir / preset_name
        preset_info = validate_archive(path)
        with ZipFile(path, "r") as archive:
            preset_text = _decode(
                _read_member(archive, FORCED_PRESET_MEMBER, f"{preset_name} member"),
                f"{preset_name}:{FORCED_PRESET_MEMBER}",
            )
        preset_values = ai_preset_values(preset_text)
        modes.append(
            {
                "preset": preset_name,
                "preset_sha256": preset_info.sha256,
                **unresolved_mode_summary(native_values, preset_values),
            }
        )

    return {
        "archive_sha256": game.archive.sha256,
        "native_vector_sha256": _vector_digest(native_values),
        "native_call_count": len(native_values),
        "modes": modes,
    }
