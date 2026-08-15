"""Combined ready patch catalog for candidate builds and CLI selection."""

from __future__ import annotations

from collections import Counter

from .advanced import ADVANCED_PATCHES
from .definitions import DIRECT_PATCHES
from .firearm_pov import POV_PATCHES
from .firearms import FIREARM_PATCHES


_all_names = [
    *DIRECT_PATCHES,
    *ADVANCED_PATCHES,
    *FIREARM_PATCHES,
    *POV_PATCHES,
]
if len(_all_names) != len(set(_all_names)):
    counts = Counter(_all_names)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    raise RuntimeError("duplicate ready patch names: " + ", ".join(duplicates))

READY_PATCHES = {
    **DIRECT_PATCHES,
    **ADVANCED_PATCHES,
    **FIREARM_PATCHES,
    **POV_PATCHES,
}

# These represent one-choice upstream controls. Candidate builds must never
# combine multiple values from the same choice group.
EXCLUSIVE_PATCH_GROUPS = (
    frozenset({"one_hit_ai", "headshot_only_ai"}),
    frozenset(
        {
            "better_firearm_pov_62",
            "better_firearm_pov_72",
            "better_firearm_pov_82",
        }
    ),
)
