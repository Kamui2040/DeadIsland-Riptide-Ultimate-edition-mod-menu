"""Combined ready patch catalog for candidate builds and CLI selection."""

from __future__ import annotations

from collections import Counter

from .advanced import ADVANCED_PATCHES
from .definitions import DIRECT_PATCHES
from .firearm_pov import POV_PATCHES
from .firearms import FIREARM_PATCHES
from .forced_spawn import FORCED_SPAWN_PATCHES
from .forced_spawn_compat import FORCED_SPAWN_COMPAT_PATCHES
from .fov import FOV_PATCHES
from .hard_ai import HARD_AI_PATCHES
from .weather import WEATHER_PATCHES
from .zombie_size import ZOMBIE_SIZE_PATCHES


_all_names = [
    *DIRECT_PATCHES,
    *ADVANCED_PATCHES,
    *HARD_AI_PATCHES,
    *FIREARM_PATCHES,
    *POV_PATCHES,
    *FOV_PATCHES,
    *ZOMBIE_SIZE_PATCHES,
    *WEATHER_PATCHES,
    *FORCED_SPAWN_PATCHES,
    *FORCED_SPAWN_COMPAT_PATCHES,
]
if len(_all_names) != len(set(_all_names)):
    counts = Counter(_all_names)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    raise RuntimeError("duplicate ready patch names: " + ", ".join(duplicates))

READY_PATCHES = {
    **DIRECT_PATCHES,
    **ADVANCED_PATCHES,
    **HARD_AI_PATCHES,
    **FIREARM_PATCHES,
    **POV_PATCHES,
    **FOV_PATCHES,
    **ZOMBIE_SIZE_PATCHES,
    **WEATHER_PATCHES,
    **FORCED_SPAWN_PATCHES,
    **FORCED_SPAWN_COMPAT_PATCHES,
}

# These represent one-choice upstream controls. Candidate builds must never
# combine multiple values from the same choice group.
EXCLUSIVE_PATCH_GROUPS = (
    frozenset({"one_hit_ai", "hard_ai", "headshot_only_ai"}),
    frozenset(
        {
            "better_firearm_pov_62",
            "better_firearm_pov_72",
            "better_firearm_pov_82",
        }
    ),
    frozenset({"camera_fov_72", "camera_fov_82"}),
    frozenset(
        {
            "zombie_size_extra_small",
            "zombie_size_midget",
            "zombie_size_large",
            "zombie_size_supersize",
        }
    ),
    frozenset(WEATHER_PATCHES),
    frozenset((*FORCED_SPAWN_PATCHES, *FORCED_SPAWN_COMPAT_PATCHES)),
)
