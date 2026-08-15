"""Hard AI semantic definition reconstructed from accepted native preset evidence."""

from __future__ import annotations

import hashlib
import json

from .advanced import AdvancedPatchDefinition, NamedCallEdit

HARD_AI_AUDIT_DIGEST = "581a922f45985380c79cc4a8dcfa0164597a2c83cac9d3e6643d05e24bb6d9d1"

# One line per changed native member. Each field is
# argument=accepted-prior>released-hard-value. This is semantic gameplay data
# only; no preset files or raw game-file content are embedded.
_HARD_AI_SPEC = """\
human/human_data.scr|arms_health_mul=1.0>1.3,head_health_influence=5.0>2.0,head_health_mul=1.0>1.3,health_mul=1.0>1.3,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,legs_health_mul=1.0>1.3,pro_player_head_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
human/human_data_preset_custom_0.scr|head_health_influence=1.0>0.4,health_mul=0.1>0.13,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
human/human_data_preset_custom_10.scr|health_mul=7.0>9.1
human/human_data_preset_custom_11.scr|head_health_influence=3.0>1.2,health_mul=7.0>9.1
human/human_data_preset_custom_12.scr|head_health_influence=1.0>0.4,health_mul=4.0>5.2,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
human/human_data_preset_custom_13.scr|health_mul=50.0>65.0
human/human_data_preset_custom_14.scr|head_health_influence=3.0>1.2,health_mul=1.0>0.4
human/human_data_preset_custom_15.scr|health_mul=0.001>0.0013
human/human_data_preset_custom_2.scr|health_mul=8.0>10.4
human/human_data_preset_custom_4.scr|health_mul=5.0>6.5
human/human_data_preset_custom_5.scr|health_mul=3.0>3.9
human/human_data_preset_custom_7.scr|head_health_influence=3.0>1.2,health_mul=7.0>9.1
infected/infected_data.scr|arms_health_mul=1.0>1.3,head_health_influence=2.0>0.8,head_health_mul=1.0>1.3,health_mul=1.0>1.3,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,legs_health_mul=1.0>1.3,pro_player_head_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
infected/infected_data_preset_custom_1.scr|health_mul=1.0>1.3
infected/infected_data_preset_custom_10.scr|head_health_influence=2.0>0.8,health_mul=4.0>5.2,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
infected/infected_data_preset_custom_12.scr|health_mul=1.5>1.95
infected/infected_data_preset_custom_13.scr|head_health_influence=1.0>0.4,health_mul=10.0>13.0
infected/infected_data_preset_custom_15.scr|health_mul=1.5>1.95
infected/infected_data_preset_custom_16.scr|head_health_influence=1.0>0.4,health_mul=2.0>2.6
infected/infected_data_preset_custom_17.scr|health_mul=1.5>1.95
infected/infected_data_preset_custom_2.scr|health_mul=1.0>1.3
infected/infected_data_preset_custom_20.scr|head_health_influence=1.0>0.4,health_mul=45.0>58.0
infected/infected_data_preset_custom_22.scr|head_health_influence=1.0>0.4,health_mul=3.5>4.16
infected/infected_data_preset_custom_23.scr|head_health_influence=1.0>0.4,health_mul=4.0>5.2,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.40
infected/infected_data_preset_custom_24.scr|head_health_influence=1.0>0.4,health_mul=10.0>13.0
infected/infected_data_preset_custom_25.scr|head_health_influence=1.0>0.4,health_mul=100.0>130.0
infected/infected_data_preset_custom_3.scr|health_mul=1.5>1.95
infected/infected_data_preset_custom_5.scr|health_mul=1.0>1.3
infected/infected_data_preset_custom_6.scr|head_health_influence=0.25>0.04,health_mul=6.0>7.8,left_arm_health_influence=0.1>0.04,left_leg_health_influence=0.1>0.04,right_arm_health_influence=0.1>0.04,right_leg_health_influence=0.1>0.04,torso_back_health_influence=1.0>0.4,torso_front_health_influence=0.1>0.04
infected/infected_data_preset_custom_8.scr|head_health_influence=1.0>0.4,health_mul=4.0>5.2,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data.scr|head_health_influence=1.25>0.5,left_arm_health_influence=1.0>0.4,left_leg_health_influence=1.0>0.4,pro_player_head_health_influence=1.0>0.4,right_arm_health_influence=1.0>0.4,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_0.scr|head_health_influence=1.0>0.4,health_mul=7.0>9.1
zombie/vessel_data_preset_custom_13.scr|health_mul=0.75>0.975
zombie/vessel_data_preset_custom_15.scr|health_mul=0.3>0.39
zombie/vessel_data_preset_custom_16.scr|head_health_influence=1.5>0.6,health_mul=3.2>4.16,left_arm_health_influence=1.0>0.4,left_leg_health_influence=0.25>0.1,right_arm_health_influence=1.0>0.4,right_leg_health_influence=0.25>0.1,torso_back_health_influence=0.75>0.3,torso_front_health_influence=0.75>0.3
zombie/vessel_data_preset_custom_18.scr|health_mul=4.0>5.2
zombie/vessel_data_preset_custom_19.scr|health_mul=3.0>3.9
zombie/vessel_data_preset_custom_20.scr|head_health_influence=2.0>0.8,health_mul=10.0>13.0,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_21.scr|head_health_influence=1.5>0.6,health_mul=2.5>3.25,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_23.scr|health_mul=10.0>13.0
zombie/vessel_data_preset_custom_24.scr|health_mul=2.0>2.6
zombie/vessel_data_preset_custom_25.scr|head_health_influence=1.5>0.6,health_mul=3.2>4.16,left_arm_health_influence=1.0>0.4,left_leg_health_influence=0.25>0.1,right_arm_health_influence=1.0>0.4,right_leg_health_influence=0.25>0.1,torso_back_health_influence=0.75>0.3,torso_front_health_influence=0.75>0.3
zombie/vessel_data_preset_custom_26.scr|head_health_influence=1.5>0.5,health_mul=2.5>3.25,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_27.scr|health_mul=3.0>3.9
zombie/vessel_data_preset_custom_29.scr|health_mul=6.0>7.8
zombie/vessel_data_preset_custom_3.scr|health_mul=1.25>1.625
zombie/vessel_data_preset_custom_30.scr|head_health_influence=1.0>0.4,health_mul=5.0>6.5,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_31.scr|head_health_influence=1.0>0.16,health_mul=10.0>13.0,left_arm_health_influence=0.5>0.08,left_leg_health_influence=1.0>0.16,right_arm_health_influence=0.5>0.08,right_leg_health_influence=1.0>0.16,torso_back_health_influence=1.0>0.16,torso_front_health_influence=1.0>0.16
zombie/vessel_data_preset_custom_32.scr|head_health_influence=1.0>0.4,health_mul=2.0>2.6,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_34.scr|health_mul=3.0>3.9
zombie/vessel_data_preset_custom_35.scr|head_health_influence=2.0>0.8,health_mul=10.0>13.0,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_4.scr|health_mul=0.75>0.975
zombie/vessel_data_preset_custom_41.scr|health_mul=0.3>0.39
zombie/vessel_data_preset_custom_42.scr|head_health_influence=1.0>0.4,health_mul=10.0>13.0,left_arm_health_influence=0.5>0.2,left_leg_health_influence=1.0>0.4,right_arm_health_influence=0.5>0.2,right_leg_health_influence=1.0>0.4,torso_back_health_influence=1.0>0.4,torso_front_health_influence=1.0>0.4
zombie/vessel_data_preset_custom_43.scr|head_health_influence=1.0>0.4,health_mul=1.7>2.21
zombie/vessel_data_preset_custom_44.scr|health_mul=7.0>9.1
zombie/vessel_data_preset_custom_5.scr|health_mul=0.75>0.975
"""


def _hard_ai_rows() -> tuple[tuple[str, str, str, str, str], ...]:
    rows: list[tuple[str, str, str, str, str]] = []
    for line in _HARD_AI_SPEC.splitlines():
        relative, encoded_edits = line.split("|", 1)
        member = "data/ai/" + relative
        for encoded in encoded_edits.split(","):
            argument, values = encoded.split("=", 1)
            expected, desired = values.split(">", 1)
            rows.append((member, "ParamFloat", argument, expected, desired))
    return tuple(rows)


HARD_AI_ROWS = _hard_ai_rows()

if len(HARD_AI_ROWS) != 209:
    raise RuntimeError("hard AI semantic table must contain exactly 209 edits")
if len({row[0] for row in HARD_AI_ROWS}) != 57:
    raise RuntimeError("hard AI semantic table must cover exactly 57 members")

_canonical = json.dumps(HARD_AI_ROWS, separators=(",", ":"))
if hashlib.sha256(_canonical.encode("utf-8")).hexdigest() != HARD_AI_AUDIT_DIGEST:
    raise RuntimeError("hard AI semantic table digest mismatch")

HARD_AI = AdvancedPatchDefinition(
    "hard_ai",
    tuple(NamedCallEdit(*row) for row in HARD_AI_ROWS),
)

HARD_AI_PATCHES = {HARD_AI.name: HARD_AI}
