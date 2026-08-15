"""Semantic camera FOV definitions reconstructed from source and native audits."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .definitions import DEFAULT_LEVELS, XmlPropertyEdit
from .errors import PatchError
from .firearms import ItemUpgradeInsertEdit
from .structured import _first_quoted_argument_block_span

INVENTORY_GEN = "data/inventory_gen.scr"
_TIER_RECOIL_MARKERS = (2, 4, 6, 8)

_TIER_RECOIL_ITEMS = (
    "Firearm_ShotgunShortGen",
    "Firearm_ShotgunGen",
    "Firearm_Shotgun_BGen",
    "Firearm_Shotgun_CGen",
    "Firearm_Shotgun_DGen",
    "Firearm_Shotgun_EGen",
    "Firearm_Shotgun_FGen",
    "Firearm_leg_CrowdPleaser",
)

_PISTOL_RECOIL_VARIANTS = {
    "Firearm_ColtGen": (
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.0095", "0.0090", "0.0085"),
    ),
    "Firearm_MagnumGen": (
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.048", "0.047", "0.046"),
    ),
    "Firearm_M9Gen": (
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.008", "0.007", "0.006"),
    ),
    "Firearm_DesertEagleGen": (
        ("0.025", "0.05", "0.05", "0.05", "0.05"),
        ("0.025", "0.05", "0.012", "0.010", "0.008"),
    ),
    "Firearm_leg_Mccall9Mm": (
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.008", "0.007", "0.006"),
    ),
}


@dataclass(frozen=True)
class ItemFirstRecoilEdit:
    member: str
    item: str
    accepted_sequences: tuple[tuple[str, ...], ...]
    desired_base: str

    def apply(self, text: str) -> str:
        start, end = _first_quoted_argument_block_span(text, "Item", self.item)
        block = text[start:end]
        pattern = re.compile(
            r'^(?![ \t]*//)(?P<prefix>[ \t]*ShootVertRecoil\(\s*)'
            r'(?P<arguments>[^\r\n)]*?)'
            r'(?P<suffix>\s*\)\s*;?[ \t]*(?://[^\r\n]*)?)(?P<cr>\r?)$',
            re.MULTILINE,
        )
        matches = list(pattern.finditer(block))
        found = tuple(match.group("arguments").strip() for match in matches)
        if found not in self.accepted_sequences:
            raise PatchError(
                f"Item {self.item} ShootVertRecoil: "
                f"unexpected source sequence {found!r}"
            )
        if not matches:
            raise PatchError(f"Item {self.item} ShootVertRecoil: no active calls")
        first = matches[0]
        new_block = (
            block[: first.start("arguments")]
            + self.desired_base
            + block[first.end("arguments") :]
        )
        return text[:start] + new_block + text[end:]


@dataclass(frozen=True)
class CameraFovPatchDefinition:
    name: str
    edits: tuple[XmlPropertyEdit | ItemFirstRecoilEdit | ItemUpgradeInsertEdit, ...]


def _tier_recoil_insert(item: str) -> ItemUpgradeInsertEdit:
    return ItemUpgradeInsertEdit(
        INVENTORY_GEN,
        item,
        tuple(
            (ordinal, ("ShootVertRecoil(0.14);",))
            for ordinal in _TIER_RECOIL_MARKERS
        ),
    )


def _camera_fov_definition(
    name: str,
    *,
    camera_value: str,
    tier_base_recoil: str,
    pistol_base_recoil: tuple[tuple[str, str], ...],
) -> CameraFovPatchDefinition:
    edits: list[XmlPropertyEdit | ItemFirstRecoilEdit | ItemUpgradeInsertEdit] = [
        XmlPropertyEdit(DEFAULT_LEVELS, "CameraDefaultFOV", "62.5", camera_value)
    ]
    for item in _TIER_RECOIL_ITEMS:
        edits.append(
            ItemFirstRecoilEdit(
                INVENTORY_GEN,
                item,
                (("0.1",),),
                tier_base_recoil,
            )
        )
        edits.append(_tier_recoil_insert(item))
    for item, desired in pistol_base_recoil:
        edits.append(
            ItemFirstRecoilEdit(
                INVENTORY_GEN,
                item,
                _PISTOL_RECOIL_VARIANTS[item],
                desired,
            )
        )
    return CameraFovPatchDefinition(name, tuple(edits))


CAMERA_FOV_72 = _camera_fov_definition(
    "camera_fov_72",
    camera_value="72",
    tier_base_recoil="0.06",
    pistol_base_recoil=(
        ("Firearm_DesertEagleGen", "0.015"),
        ("Firearm_MagnumGen", "0.017"),
        ("Firearm_M9Gen", "0.015"),
        ("Firearm_leg_Mccall9Mm", "0.015"),
    ),
)

CAMERA_FOV_82 = _camera_fov_definition(
    "camera_fov_82",
    camera_value="82",
    tier_base_recoil="0.033",
    pistol_base_recoil=(
        ("Firearm_DesertEagleGen", "0.008"),
        ("Firearm_MagnumGen", "0.010"),
        ("Firearm_M9Gen", "0.015"),
        ("Firearm_leg_Mccall9Mm", "0.015"),
        ("Firearm_ColtGen", "0.015"),
    ),
)

# Released active-write accounting:
# 72 = camera + 8 firearm groups * 5 recoil writes + 4 pistol base writes.
# 82 = camera + 8 firearm groups * 5 recoil writes + 5 pistol base writes.
FOV72_RELEASED_WRITE_COUNT = 45
FOV82_RELEASED_WRITE_COUNT = 46

FOV_PATCHES = {
    CAMERA_FOV_72.name: CAMERA_FOV_72,
    CAMERA_FOV_82.name: CAMERA_FOV_82,
}
