"""Sanitized AI-source token research for unresolved forced-spawn modes."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from .archive import validate_archive
from .errors import ValidationError
from .game import validate_game_root
from .spawn_member_recipe_audit import quoted_values
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

# Narrow, semantically related native sources only. These members already
# participate in AI/spawn/preset identity and have been audited elsewhere in
# the parity work. This intentionally does not scan arbitrary Data0 strings.
_AI_SOURCE_MEMBERS = (
    FORCED_NATIVE_MEMBER,
    "data/presets/zombieai.pre",
    "data/presets/zombieai_pre.def",
    "data/presets/infectedai.pre",
    "data/presets/infectedai_pre.def",
    "data/bestiary.scr",
)


def _digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _vector_digest(values: tuple[str, ...]) -> str:
    canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _decode(data: bytes, identity: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode AI-source spawn audit target: {identity}") from exc


def _read_member(archive: ZipFile, member: str, identity: str) -> bytes:
    if member not in archive.namelist():
        raise ValidationError(f"AI-source spawn audit missing {identity}: {member}")
    return archive.read(member)


@dataclass(frozen=True)
class _AITokenSource:
    member: str
    value_sha256: str
    part_index: int


def _ai_token_sources(native_members: dict[str, str]) -> dict[str, _AITokenSource]:
    choices: dict[str, list[_AITokenSource]] = {}
    for member in sorted(native_members):
        for value in quoted_values(native_members[member]):
            value_digest = _digest_text(value)
            for part_index, part in enumerate(_parts(value)):
                if not _is_token(part):
                    continue
                choices.setdefault(part, []).append(
                    _AITokenSource(
                        member=member,
                        value_sha256=value_digest,
                        part_index=part_index,
                    )
                )

    sources: dict[str, _AITokenSource] = {}
    for token, token_choices in choices.items():
        sources[token] = min(
            token_choices,
            key=lambda source: (
                source.member,
                source.value_sha256,
                source.part_index,
            ),
        )
    return sources


def _candidate_recipe(
    native_spawn_values: tuple[str, ...],
    target: str,
    base_ordinal: int,
    token_sources: dict[str, _AITokenSource],
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
                "donor_member": source.member,
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
        raise ValidationError("AI-source spawn reconstruction did not match target")

    return {
        "base_ordinal": base_ordinal,
        "base_value_sha256": _digest_text(base),
        "part_count": len(base_parts),
        "replacement_count": len(replacements),
        "replacements": replacements,
        "reconstructed_sha256": _digest_text(rebuilt),
    }


def ai_source_recipe_summary(
    native_spawn_values: tuple[str, ...],
    native_members: dict[str, str],
    target: str,
) -> dict[str, object]:
    """Find a whole-token recipe from the bounded native AI source set."""
    if len(native_spawn_values) != 165:
        raise ValidationError("AI-source spawn audit requires 165 native spawn values")
    if set(native_members) != set(_AI_SOURCE_MEMBERS):
        raise ValidationError("AI-source spawn audit received an unexpected source-member set")

    quoted = tuple(
        value
        for member in sorted(native_members)
        for value in quoted_values(native_members[member])
    )
    if not quoted:
        raise ValidationError("AI-source spawn audit found no quoted strings")
    if target in quoted:
        raise ValidationError(
            "AI-source spawn audit target already exists as an exact quoted donor"
        )

    token_sources = _ai_token_sources(native_members)
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
                    str(change["donor_member"]),
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


def _mode_summary(
    native_values: tuple[str, ...],
    native_members: dict[str, str],
    preset_values: tuple[str, ...],
) -> dict[str, object]:
    if len(native_values) != 165 or len(preset_values) != 165:
        raise ValidationError("AI-source spawn audit requires exactly 165 values")

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
            "AI-source spawn audit expected one repeated desired identifier"
        )
    target, changed_occurrences = next(iter(desired.items()))
    return {
        "changed_count": len(changed_ordinals),
        "changed_occurrences": changed_occurrences,
        "preserved_ordinals": list(preserved_ordinals),
        **ai_source_recipe_summary(native_values, native_members, target),
    }


def audit_ai_source_spawn_recipes(root: Path, preset_dir: Path) -> dict[str, object]:
    """Audit bounded cross-member AI token recipes for the four remaining modes."""
    game = validate_game_root(root)
    preset_dir = Path(preset_dir)

    native_bytes: dict[str, bytes] = {}
    native_text: dict[str, str] = {}
    with ZipFile(game.data0, "r") as archive:
        for member in _AI_SOURCE_MEMBERS:
            data = _read_member(archive, member, member)
            native_bytes[member] = data
            native_text[member] = _decode(data, member)

    native_values = ai_preset_values(native_text[FORCED_NATIVE_MEMBER])
    if len(native_values) != 165:
        raise ValidationError(
            f"AI-source spawn audit expected 165 native values, found {len(native_values)}"
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
                **_mode_summary(native_values, native_text, preset_values),
            }
        )

    source_summary = {
        member: {
            "sha256": sha256(native_bytes[member]).hexdigest(),
            "quoted_string_count": len(quoted_values(native_text[member])),
        }
        for member in _AI_SOURCE_MEMBERS
    }

    return {
        "archive_sha256": game.archive.sha256,
        "native_vector_sha256": _vector_digest(native_values),
        "native_call_count": len(native_values),
        "source_members": source_summary,
        "modes": modes,
    }
