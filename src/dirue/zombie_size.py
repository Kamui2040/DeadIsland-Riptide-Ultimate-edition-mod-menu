"""Semantic zombie-size definitions reconstructed from hardened preset audits."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re

from .errors import PatchError


def _sequence_digest(values: tuple[str, ...]) -> str:
    return sha256("\n".join(values).encode("utf-8")).hexdigest()


def replace_scale_sequence(
    text: str,
    *,
    call_name: str,
    field_name: str,
    expected_count: int,
    expected_digest: str,
    desired_value: str,
) -> str:
    """Replace one validated scale-field sequence while preserving unrelated text."""
    if expected_count < 1:
        raise PatchError(f"{call_name} {field_name}: expected count must be positive")
    pattern = re.compile(
        rf'^(?![ \t]*//)(?P<prefix>[ \t]*{re.escape(call_name)}\(\s*'
        rf'"{re.escape(field_name)}"\s*,\s*")'
        r'(?P<value>[^"\r\n]+)'
        r'(?P<suffix>"\s*\)\s*[,;]?[ \t]*(?://[^\r\n]*)?)(?P<cr>\r?)$',
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    values = tuple(match.group("value").strip() for match in matches)
    if len(values) != expected_count:
        raise PatchError(
            f"{call_name} {field_name}: expected {expected_count} active calls, "
            f"found {len(values)}"
        )
    actual_digest = _sequence_digest(values)
    if actual_digest != expected_digest:
        raise PatchError(
            f"{call_name} {field_name}: source value sequence did not match "
            "the verified native baseline"
        )

    def replacement(match: re.Match[str]) -> str:
        return (
            f'{match.group("prefix")}{desired_value}{match.group("suffix")}'
            f'{match.group("cr")}'
        )

    updated, count = pattern.subn(replacement, text)
    if count != expected_count:
        raise PatchError(
            f"{call_name} {field_name}: expected {expected_count} replacements, "
            f"made {count}"
        )
    return updated


@dataclass(frozen=True)
class ScaleSequenceEdit:
    member: str
    call_name: str
    field_name: str
    expected_count: int
    expected_digest: str
    desired_value: str

    def apply(self, text: str) -> str:
        return replace_scale_sequence(
            text,
            call_name=self.call_name,
            field_name=self.field_name,
            expected_count=self.expected_count,
            expected_digest=self.expected_digest,
            desired_value=self.desired_value,
        )


@dataclass(frozen=True)
class ZombieSizePatchDefinition:
    name: str
    edits: tuple[ScaleSequenceEdit, ...]


# Counts and SHA-256 digests describe only the verified native value sequences.
# They let runtime validation fail closed without embedding proprietary preset files
# or copying the native value vectors into the repository.
_BASELINE_SCALE_SEQUENCES = (
    (
        "data/presets/infectedai.pre",
        "AddField",
        "m_ForcedBodyScaleMax",
        1,
        "cf9dcf6da8a82be1335c398a4005def7ee3a53d4698c59dbc6b2b14e72d1263c",
    ),
    (
        "data/presets/infectedai.pre",
        "AddField",
        "m_ForcedBodyScaleMin",
        1,
        "cf9dcf6da8a82be1335c398a4005def7ee3a53d4698c59dbc6b2b14e72d1263c",
    ),
    (
        "data/presets/infectedai_pre.def",
        "SetField",
        "m_ForcedBodyScaleMax",
        119,
        "10e49d62305b783607b769d73e82f6435c8bbe8248aff37d5728106a6cc4e38e",
    ),
    (
        "data/presets/infectedai_pre.def",
        "SetField",
        "m_ForcedBodyScaleMin",
        119,
        "bb96d84161994795453b202ab9e6123ae68274a5922152df9e2be17fccbd9d14",
    ),
    (
        "data/presets/zombieai.pre",
        "AddField",
        "m_ForcedBodyScaleMax",
        1,
        "3cae67a480a375359869d8b9bff239f8af5f08bef645d3d86747f1223c71357b",
    ),
    (
        "data/presets/zombieai.pre",
        "AddField",
        "m_ForcedBodyScaleMin",
        1,
        "3cae67a480a375359869d8b9bff239f8af5f08bef645d3d86747f1223c71357b",
    ),
    (
        "data/presets/zombieai_pre.def",
        "SetField",
        "m_ForcedBodyScaleMax",
        183,
        "0687d9f74b05c83640ed99e10ce25a3d5dab5fbc724dfbd9dae02376f0d407e7",
    ),
    (
        "data/presets/zombieai_pre.def",
        "SetField",
        "m_ForcedBodyScaleMin",
        183,
        "1722b67d65d2bd3c5f94bc2eb9b111b95e7d2ccad7dcb775b02992ecf2209314",
    ),
)


def _size_definition(name: str, desired_value: str) -> ZombieSizePatchDefinition:
    return ZombieSizePatchDefinition(
        name,
        tuple(
            ScaleSequenceEdit(
                member,
                call_name,
                field_name,
                count,
                digest,
                desired_value,
            )
            for member, call_name, field_name, count, digest
            in _BASELINE_SCALE_SEQUENCES
        ),
    )


ZOMBIE_SIZE_EXTRA_SMALL = _size_definition("zombie_size_extra_small", "0.3")
ZOMBIE_SIZE_MIDGET = _size_definition("zombie_size_midget", "0.6")
ZOMBIE_SIZE_LARGE = _size_definition("zombie_size_large", "2.0")
ZOMBIE_SIZE_SUPERSIZE = _size_definition("zombie_size_supersize", "5.0")

ZOMBIE_SIZE_PATCHES = {
    definition.name: definition
    for definition in (
        ZOMBIE_SIZE_EXTRA_SMALL,
        ZOMBIE_SIZE_MIDGET,
        ZOMBIE_SIZE_LARGE,
        ZOMBIE_SIZE_SUPERSIZE,
    )
}
