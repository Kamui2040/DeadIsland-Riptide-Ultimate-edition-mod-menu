"""Public-safe semantic transforms for forced-spawn modes."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .definitions import PatchDefinition
from .errors import PatchError


FORCED_SPAWN_MEMBER = "data/presets/aispawnbox_pre.def"
_NATIVE_VECTOR_SHA256 = "f162dabf233daab2954daf124a673d8beaca2ef92ead2620e9606b00a2dfaebf"

_AI_PRESET_PATTERN = re.compile(
    r'^(?![ \t]*//)'
    r'(?P<prefix>[ \t]*SetField\([ \t]*"m_AIPresets"[ \t]*,[ \t]*")'
    r'(?P<value>[^"\r\n]*)'
    r'(?P<suffix>"[ \t]*\)[ \t]*[,;]?[ \t]*(?://[^\r\n]*)?(?:\r?\n|$))',
    re.MULTILINE,
)
_PART_PATTERN = re.compile(r"[A-Za-z0-9]+|[^A-Za-z0-9]+")


def _value_digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _vector_digest(values: tuple[str, ...]) -> str:
    canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _parts(value: str) -> tuple[str, ...]:
    parts = tuple(_PART_PATTERN.findall(value))
    if "".join(parts) != value:
        raise PatchError("forced spawn: identifier tokenizer did not round-trip")
    return parts


def _is_token(part: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9]+", part) is not None


def _native_values(text: str) -> tuple[list[re.Match[str]], tuple[str, ...]]:
    matches = list(_AI_PRESET_PATTERN.finditer(text))
    if len(matches) != 165:
        raise PatchError(
            "forced spawn: expected 165 active m_AIPresets calls, "
            f"found {len(matches)}"
        )
    values = tuple(match.group("value") for match in matches)
    if _vector_digest(values) != _NATIVE_VECTOR_SHA256:
        raise PatchError(
            "forced spawn: native m_AIPresets vector does not match audited baseline"
        )
    return matches, values


def _replace_ordinals(
    text: str,
    matches: list[re.Match[str]],
    ordinals: list[int],
    desired: str,
) -> str:
    updated = text
    spans = [
        (
            matches[ordinal - 1].start("value"),
            matches[ordinal - 1].end("value"),
        )
        for ordinal in ordinals
    ]
    for start, end in reversed(spans):
        updated = updated[:start] + desired + updated[end:]
    return updated


@dataclass(frozen=True)
class ForcedSpawnDonorEdit:
    """Replace audited call ordinals using one pristine same-member donor value."""

    member: str
    donor_ordinal: int
    donor_sha256: str
    preserved_ordinals: tuple[int, ...]
    expected_changed_count: int

    def apply(self, text: str) -> str:
        matches, values = _native_values(text)

        if not 1 <= self.donor_ordinal <= len(values):
            raise PatchError("forced spawn: donor ordinal is outside the audited vector")
        preserved = set(self.preserved_ordinals)
        if self.donor_ordinal not in preserved:
            raise PatchError("forced spawn: donor ordinal must remain preserved")
        if any(ordinal < 1 or ordinal > len(values) for ordinal in preserved):
            raise PatchError("forced spawn: preserved ordinal is outside the audited vector")

        donor = values[self.donor_ordinal - 1]
        if _value_digest(donor) != self.donor_sha256:
            raise PatchError("forced spawn: audited donor value digest does not match")

        changed_ordinals = [
            ordinal for ordinal in range(1, len(values) + 1) if ordinal not in preserved
        ]
        actual_changed = sum(
            values[ordinal - 1] != donor for ordinal in changed_ordinals
        )
        if actual_changed != self.expected_changed_count:
            raise PatchError(
                "forced spawn: audited changed-call count no longer matches pristine data"
            )

        updated = _replace_ordinals(text, matches, changed_ordinals, donor)

        result_matches = list(_AI_PRESET_PATTERN.finditer(updated))
        if len(result_matches) != 165:
            raise PatchError("forced spawn: result changed the m_AIPresets call count")
        result_values = tuple(match.group("value") for match in result_matches)
        for ordinal in preserved:
            if result_values[ordinal - 1] != values[ordinal - 1]:
                raise PatchError("forced spawn: preserved call changed unexpectedly")
        for ordinal in changed_ordinals:
            if result_values[ordinal - 1] != donor:
                raise PatchError("forced spawn: donor replacement validation failed")
        return updated


@dataclass(frozen=True)
class TokenRecipeReplacement:
    """Copy one whole identifier token from an audited pristine value."""

    part_index: int
    donor_ordinal: int
    donor_part_index: int
    donor_value_sha256: str
    token_length: int


@dataclass(frozen=True)
class ForcedSpawnRecipeEdit:
    """Reconstruct one released identifier entirely from pristine native tokens."""

    member: str
    base_ordinal: int
    base_value_sha256: str
    part_count: int
    replacements: tuple[TokenRecipeReplacement, ...]
    target_sha256: str
    preserved_ordinals: tuple[int, ...]
    expected_changed_count: int

    def apply(self, text: str) -> str:
        matches, values = _native_values(text)

        if not 1 <= self.base_ordinal <= len(values):
            raise PatchError("forced spawn: recipe base ordinal is outside the audited vector")
        base = values[self.base_ordinal - 1]
        if _value_digest(base) != self.base_value_sha256:
            raise PatchError("forced spawn: recipe base value digest does not match")

        base_parts = list(_parts(base))
        if len(base_parts) != self.part_count:
            raise PatchError("forced spawn: recipe base token shape does not match")

        replacement_indexes = [replacement.part_index for replacement in self.replacements]
        if len(replacement_indexes) != len(set(replacement_indexes)):
            raise PatchError("forced spawn: recipe repeats a target token position")

        for replacement in self.replacements:
            if not 0 <= replacement.part_index < len(base_parts):
                raise PatchError("forced spawn: recipe target token position is invalid")
            if not _is_token(base_parts[replacement.part_index]):
                raise PatchError("forced spawn: recipe would replace identifier punctuation")
            if not 1 <= replacement.donor_ordinal <= len(values):
                raise PatchError("forced spawn: recipe donor ordinal is outside the audited vector")

            donor = values[replacement.donor_ordinal - 1]
            if _value_digest(donor) != replacement.donor_value_sha256:
                raise PatchError("forced spawn: recipe donor value digest does not match")
            donor_parts = _parts(donor)
            if not 0 <= replacement.donor_part_index < len(donor_parts):
                raise PatchError("forced spawn: recipe donor token position is invalid")
            token = donor_parts[replacement.donor_part_index]
            if not _is_token(token):
                raise PatchError("forced spawn: recipe donor part is not a whole token")
            if len(token) != replacement.token_length:
                raise PatchError("forced spawn: recipe donor token length does not match")
            base_parts[replacement.part_index] = token

        desired = "".join(base_parts)
        if _value_digest(desired) != self.target_sha256:
            raise PatchError("forced spawn: reconstructed target digest does not match")

        preserved = set(self.preserved_ordinals)
        if not preserved:
            raise PatchError("forced spawn: recipe must preserve at least one audited call")
        if any(ordinal < 1 or ordinal > len(values) for ordinal in preserved):
            raise PatchError("forced spawn: preserved ordinal is outside the audited vector")

        changed_ordinals = [
            ordinal for ordinal in range(1, len(values) + 1) if ordinal not in preserved
        ]
        actual_changed = sum(
            values[ordinal - 1] != desired for ordinal in changed_ordinals
        )
        if actual_changed != self.expected_changed_count:
            raise PatchError(
                "forced spawn: reconstructed changed-call count no longer matches pristine data"
            )

        updated = _replace_ordinals(text, matches, changed_ordinals, desired)
        result_matches = list(_AI_PRESET_PATTERN.finditer(updated))
        if len(result_matches) != 165:
            raise PatchError("forced spawn: result changed the m_AIPresets call count")
        result_values = tuple(match.group("value") for match in result_matches)
        for ordinal in preserved:
            if result_values[ordinal - 1] != values[ordinal - 1]:
                raise PatchError("forced spawn: preserved call changed unexpectedly")
        for ordinal in changed_ordinals:
            if result_values[ordinal - 1] != desired:
                raise PatchError("forced spawn: recipe replacement validation failed")
        return updated


FORCE_SUICIDERS = PatchDefinition(
    "force_suiciders",
    (
        ForcedSpawnDonorEdit(
            FORCED_SPAWN_MEMBER,
            donor_ordinal=6,
            donor_sha256="eaa57a591c460bc45db948d5d4b284ed07ad290256ef201a37bc4197d918565d",
            preserved_ordinals=(6,),
            expected_changed_count=164,
        ),
    ),  # type: ignore[arg-type]
)

FORCE_BANDITS_GUNS = PatchDefinition(
    "force_bandits_guns",
    (
        ForcedSpawnDonorEdit(
            FORCED_SPAWN_MEMBER,
            donor_ordinal=119,
            donor_sha256="2624988a60c5ce564006d96fdc6dc9fd28c918ec43a492e1f625c59c5ffb6209",
            preserved_ordinals=(60, 119),
            expected_changed_count=163,
        ),
    ),  # type: ignore[arg-type]
)

FORCE_BANDITS_MELEE = PatchDefinition(
    "force_bandits_melee",
    (
        ForcedSpawnRecipeEdit(
            FORCED_SPAWN_MEMBER,
            base_ordinal=40,
            base_value_sha256="7be729fe4c99185b8a7cfe88d2e23d066157321ce33a0ed9109b6d5edad9c391",
            part_count=47,
            replacements=(
                TokenRecipeReplacement(
                    part_index=4,
                    donor_ordinal=37,
                    donor_part_index=34,
                    donor_value_sha256="6825e9b693faadffbfe4db53cc52f8c67e651f7735651f471ef16f5e83f18997",
                    token_length=13,
                ),
                TokenRecipeReplacement(
                    part_index=12,
                    donor_ordinal=37,
                    donor_part_index=4,
                    donor_value_sha256="6825e9b693faadffbfe4db53cc52f8c67e651f7735651f471ef16f5e83f18997",
                    token_length=13,
                ),
                TokenRecipeReplacement(
                    part_index=20,
                    donor_ordinal=37,
                    donor_part_index=10,
                    donor_value_sha256="6825e9b693faadffbfe4db53cc52f8c67e651f7735651f471ef16f5e83f18997",
                    token_length=13,
                ),
                TokenRecipeReplacement(
                    part_index=28,
                    donor_ordinal=37,
                    donor_part_index=16,
                    donor_value_sha256="6825e9b693faadffbfe4db53cc52f8c67e651f7735651f471ef16f5e83f18997",
                    token_length=13,
                ),
                TokenRecipeReplacement(
                    part_index=36,
                    donor_ordinal=37,
                    donor_part_index=22,
                    donor_value_sha256="6825e9b693faadffbfe4db53cc52f8c67e651f7735651f471ef16f5e83f18997",
                    token_length=13,
                ),
                TokenRecipeReplacement(
                    part_index=44,
                    donor_ordinal=37,
                    donor_part_index=28,
                    donor_value_sha256="6825e9b693faadffbfe4db53cc52f8c67e651f7735651f471ef16f5e83f18997",
                    token_length=13,
                ),
            ),
            target_sha256="77ab5589e4c2a6722f2bbad894781791a18d19ccfb87d6545e409a9caa1ecccb",
            preserved_ordinals=(60,),
            expected_changed_count=164,
        ),
    ),  # type: ignore[arg-type]
)

FORCED_SPAWN_PATCHES = {
    FORCE_SUICIDERS.name: FORCE_SUICIDERS,
    FORCE_BANDITS_GUNS.name: FORCE_BANDITS_GUNS,
    FORCE_BANDITS_MELEE.name: FORCE_BANDITS_MELEE,
}
