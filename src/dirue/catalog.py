"""Combined ready patch catalog for candidate builds and CLI selection."""

from __future__ import annotations

from .advanced import ADVANCED_PATCHES
from .definitions import DIRECT_PATCHES


_overlap = set(DIRECT_PATCHES) & set(ADVANCED_PATCHES)
if _overlap:
    raise RuntimeError("duplicate ready patch names: " + ", ".join(sorted(_overlap)))

READY_PATCHES = {**DIRECT_PATCHES, **ADVANCED_PATCHES}
