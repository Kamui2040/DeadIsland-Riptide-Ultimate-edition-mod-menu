"""Minimal functional compatibility identifiers for released forced-spawn modes."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .definitions import PatchDefinition
from .errors import PatchError
from .forced_spawn import (
    FORCED_SPAWN_MEMBER,
    _AI_PRESET_PATTERN,
    _native_values,
    _replace_ordinals,
    _value_digest,
)


_IDENTIFIER_LIST_PATTERN = re.compile(r"[A-Za-z0-9_]+(?:;[A-Za-z0-9_]+)*;?")


@dataclass(frozen=True)
class ForcedSpawnCompatibilityEdit:
    """Apply an audited minimal compatibility identifier list to spawn calls."""

    member: str
    desired_value: str
    desired_sha256: str
    expected_identifier_count: int
    preserved_ordinals: tuple[int, ...]
    expected_changed_count: int

    def apply(self, text: str) -> str:
        matches, values = _native_values(text)
        desired = self.desired_value
        if _value_digest(desired) != self.desired_sha256:
            raise PatchError("forced spawn: compatibility identifier digest does not match")
        if _IDENTIFIER_LIST_PATTERN.fullmatch(desired) is None:
            raise PatchError("forced spawn: compatibility identifier syntax is invalid")
        identifiers = tuple(identifier for identifier in desired.split(";") if identifier)
        if len(identifiers) != self.expected_identifier_count:
            raise PatchError("forced spawn: compatibility identifier count does not match")
        preserved = set(self.preserved_ordinals)
        if not preserved:
            raise PatchError("forced spawn: compatibility transform must preserve a call")
        if any(ordinal < 1 or ordinal > len(values) for ordinal in preserved):
            raise PatchError("forced spawn: preserved ordinal is outside the audited vector")
        changed_ordinals = [
            ordinal for ordinal in range(1, len(values) + 1) if ordinal not in preserved
        ]
        actual_changed = sum(values[ordinal - 1] != desired for ordinal in changed_ordinals)
        if actual_changed != self.expected_changed_count:
            raise PatchError(
                "forced spawn: compatibility changed-call count no longer matches pristine data"
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
                raise PatchError("forced spawn: compatibility replacement validation failed")
        return updated


# These values are the minimum machine-facing identifiers required to reproduce
# four released DIRUE choices. They were extracted read-only from inherited
# upstream preset blobs; no preset archive or replacement file is reused.
FORCE_BUTCHERS = PatchDefinition(
    "force_butchers",
    (
        ForcedSpawnCompatibilityEdit(
            FORCED_SPAWN_MEMBER,
            "BS_BossInfectedMeleeFighter;BS_BossInfectedMeleeDrowner",
            "ec4d6bedc647b7d142c57da6c56e83338601b2c999b80cca08429bdb18f5d951",
            2,
            (60,),
            164,
        ),
    ),  # type: ignore[arg-type]
)
FORCE_RAMS = PatchDefinition(
    "force_rams",
    (
        ForcedSpawnCompatibilityEdit(
            FORCED_SPAWN_MEMBER,
            "BS_BossInfectedRamer;BS_BossInfectedRamerSmall",
            "e130867801c23bfee629df6ab83b4f1f353710c1cf89c62f081c67f08afd0caf",
            2,
            (60,),
            164,
        ),
    ),  # type: ignore[arg-type]
)
FORCE_BLOATERS = PatchDefinition(
    "force_bloaters",
    (
        ForcedSpawnCompatibilityEdit(
            FORCED_SPAWN_MEMBER,
            "BS_BossZombieCorruptor;BS_J_BossZombieCorruptor;BS_BossZombieCorruptor_Bunker",
            "b6108d8f2f9ef99dee5440626562e53625b8b7de83de7eafacf8cef1eb3e601a",
            3,
            (60,),
            164,
        ),
    ),  # type: ignore[arg-type]
)
FORCE_THUGS = PatchDefinition(
    "force_thugs",
    (
        ForcedSpawnCompatibilityEdit(
            FORCED_SPAWN_MEMBER,
            (
                "BS_T_BossThug_001;BS_T_MiniBoss_Thug_001;BS_T_MiniBoss_Thug_002;"
                "BS_Church_Miniboss_Thug_001;BS_J_DeadZone_thugattk;BS_J_Thug_Bunker;"
                "BS_J_BossThug_003_Bunker;BS_T_BossThug_002;BS_T_BossThug_Soldier;"
                "BS_T_BossThug_003_Police;BS_T_BossThug_004_Guard;BS_T_BossThug_005_Military;"
                "BS_T_BossThug_006_Armor;"
            ),
            "efdbf3422daec1a9c960453a957ab5149383973ca97bcfb1c3e8f3cf3bff7f92",
            13,
            (60,),
            164,
        ),
    ),  # type: ignore[arg-type]
)

FORCED_SPAWN_COMPAT_PATCHES = {
    definition.name: definition
    for definition in (FORCE_BUTCHERS, FORCE_RAMS, FORCE_BLOATERS, FORCE_THUGS)
}
