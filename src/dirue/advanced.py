"""Native-verified semantic definitions reconstructed from read-only QA."""

from __future__ import annotations

from dataclasses import dataclass

from .patches import replace_named_call_value
from .structured import replace_call_sequence_in_named_block


@dataclass(frozen=True)
class NamedCallEdit:
    member: str
    call_name: str
    argument: str
    expected_value: str
    desired_value: str

    def apply(self, text: str) -> str:
        return replace_named_call_value(
            text,
            self.call_name,
            self.argument,
            self.expected_value,
            self.desired_value,
        )


@dataclass(frozen=True)
class NamedBlockCallEdit:
    member: str
    block_call: str
    block_name: str
    call_name: str
    expected_arguments: tuple[str, ...]
    desired_arguments: tuple[str, ...]

    def apply(self, text: str) -> str:
        return replace_call_sequence_in_named_block(
            text,
            block_call=self.block_call,
            block_name=self.block_name,
            call_name=self.call_name,
            expected_arguments=self.expected_arguments,
            desired_arguments=self.desired_arguments,
        )


@dataclass(frozen=True)
class AdvancedPatchDefinition:
    name: str
    edits: tuple[NamedCallEdit | NamedBlockCallEdit, ...]


CAR_PHYSICS = "data/odephysics/vehicle/cardi.phx"
OLD_BOAT_PHYSICS = "data/odephysics/vehicle/old_boat_a.phx"


# The released handler edits line 77/91 in cardi.phx and 64/78 in
# old_boat_a.phx. The native read-only audit mapped those historical line
# identities to the SimpleObjects and NonODEObjects ContactParams blocks.
NOCLIP_VEHICLES = AdvancedPatchDefinition(
    "noclip_vehicles",
    tuple(
        NamedBlockCallEdit(
            member,
            "ContactParams",
            block,
            "Ignore",
            ("0",),
            ("1",),
        )
        for member in (CAR_PHYSICS, OLD_BOAT_PHYSICS)
        for block in ("SimpleObjects", "NonODEObjects")
    ),
)


# The released one-hit preset differs from the native AI tree only by these
# two named values plus non-behavioral trailing annotations. The native v4
# read-only preset audit verified the complete pair.
ONE_HIT_AI = AdvancedPatchDefinition(
    "one_hit_ai",
    (
        NamedCallEdit(
            "data/ai/infected/infected_data.scr",
            "ParamBool",
            "one_shot",
            "0",
            "1",
        ),
        NamedCallEdit(
            "data/ai/zombie/vessel_data.scr",
            "ParamBool",
            "one_shot",
            "0",
            "1",
        ),
    ),
)


_HEADSHOT_FIELDS = (
    "left_arm_health_influence",
    "left_leg_health_influence",
    "right_arm_health_influence",
    "right_leg_health_influence",
    "torso_back_health_influence",
    "torso_front_health_influence",
)

_HEADSHOT_STANDARD = (
    "data/ai/human/human_data.scr",
    "data/ai/human/human_data_preset_custom_0.scr",
    "data/ai/human/human_data_preset_custom_12.scr",
    "data/ai/infected/infected_data.scr",
    "data/ai/infected/infected_data_preset_custom_10.scr",
    "data/ai/infected/infected_data_preset_custom_23.scr",
    "data/ai/infected/infected_data_preset_custom_8.scr",
    "data/ai/zombie/vessel_data.scr",
)

_HEADSHOT_INFECTED6 = "data/ai/infected/infected_data_preset_custom_6.scr"

_HEADSHOT_VESSEL_A = (
    "data/ai/zombie/vessel_data_preset_custom_16.scr",
    "data/ai/zombie/vessel_data_preset_custom_25.scr",
)

_HEADSHOT_VESSEL_B = (
    "data/ai/zombie/vessel_data_preset_custom_20.scr",
    "data/ai/zombie/vessel_data_preset_custom_21.scr",
    "data/ai/zombie/vessel_data_preset_custom_26.scr",
    "data/ai/zombie/vessel_data_preset_custom_30.scr",
    "data/ai/zombie/vessel_data_preset_custom_31.scr",
    "data/ai/zombie/vessel_data_preset_custom_32.scr",
    "data/ai/zombie/vessel_data_preset_custom_35.scr",
    "data/ai/zombie/vessel_data_preset_custom_42.scr",
)


def _health_edits(member: str, values: tuple[str, ...]) -> tuple[NamedCallEdit, ...]:
    if len(values) != len(_HEADSHOT_FIELDS):
        raise ValueError("headshot prior-state vector has the wrong length")
    return tuple(
        NamedCallEdit(member, "ParamFloat", field, old, "0.0")
        for field, old in zip(_HEADSHOT_FIELDS, values)
    )


# Every changed member in the released headshot preset was classified as a
# named-value-only difference by the native read-only preset audit. No copied
# preset file content is used here.
HEADSHOT_ONLY_AI = AdvancedPatchDefinition(
    "headshot_only_ai",
    tuple(
        edit
        for member in _HEADSHOT_STANDARD
        for edit in _health_edits(member, ("1.0",) * 6)
    )
    + _health_edits(
        _HEADSHOT_INFECTED6,
        ("0.1", "0.1", "0.1", "0.1", "1.0", "0.1"),
    )
    + (
        NamedCallEdit(
            "data/ai/zombie/vessel_data_preset_custom_14.scr",
            "ParamBool",
            "one_shot",
            "1",
            "0",
        ),
    )
    + tuple(
        edit
        for member in _HEADSHOT_VESSEL_A
        for edit in _health_edits(
            member,
            ("1.0", "0.25", "1.0", "0.25", "0.75", "0.75"),
        )
    )
    + tuple(
        edit
        for member in _HEADSHOT_VESSEL_B
        for edit in _health_edits(
            member,
            ("0.5", "1.0", "0.5", "1.0", "1.0", "1.0"),
        )
    ),
)


ADVANCED_PATCHES = {
    definition.name: definition
    for definition in (NOCLIP_VEHICLES, ONE_HIT_AI, HEADSHOT_ONLY_AI)
}
