"""Public-safe semantic transforms for donor-backed forced-spawn modes."""

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


def _value_digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _vector_digest(values: tuple[str, ...]) -> str:
    canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ForcedSpawnDonorEdit:
    """Replace audited call ordinals using one pristine same-member donor value."""

    member: str
    donor_ordinal: int
    donor_sha256: str
    preserved_ordinals: tuple[int, ...]
    expected_changed_count: int

    def apply(self, text: str) -> str:
        matches = list(_AI_PRESET_PATTERN.finditer(text))
        if len(matches) != 165:
            raise PatchError(
                "forced spawn: expected 165 active m_AIPresets calls, "
                f"found {len(matches)}"
            )

        values = tuple(match.group("value") for match in matches)
        actual_vector_digest = _vector_digest(values)
        if actual_vector_digest != _NATIVE_VECTOR_SHA256:
            raise PatchError(
                "forced spawn: native m_AIPresets vector does not match audited baseline"
            )

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

        updated = text
        replacements = [
            (
                matches[ordinal - 1].start("value"),
                matches[ordinal - 1].end("value"),
            )
            for ordinal in changed_ordinals
        ]
        for start, end in reversed(replacements):
            updated = updated[:start] + donor + updated[end:]

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

FORCED_SPAWN_PATCHES = {
    FORCE_SUICIDERS.name: FORCE_SUICIDERS,
    FORCE_BANDITS_GUNS.name: FORCE_BANDITS_GUNS,
}
