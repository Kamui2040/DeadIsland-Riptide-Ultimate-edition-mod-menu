import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from dirue.audit import (
    CHARACTER_SKILLS,
    DEFAULT_LEVELS,
    GLOW_SCD,
    GLOW_SCR,
    CAR_PHYSICS,
    OLD_BOAT_PHYSICS,
    GAME_AUDIO_EFFECTS,
    DEFAULT_LOOT,
    INVENTORY_GEN,
    INVENTORY_SPECIAL,
    INTRO_MOVIES,
    DEFAULT_LEVEL_PROPERTIES,
    audit_data0,
)


class AuditZipTests(unittest.TestCase):
    def test_read_only_audit_on_synthetic_archive(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Data0.pak"
            props = "\n".join(
                f'<prop n="{name}" v="1"/>' for name in DEFAULT_LEVEL_PROPERTIES
            )
            skill = '<skill id="DeeperPockets" desc_params="2;4;6"><effect id="InventorySize" change="2"/></skill>'
            loot = 'Loot("Chest")\n{\n' + "\n".join(
                [
                    'ColorWeight(Color_White, 91)',
                    'ColorWeight(Color_Green, 7)',
                    'ColorWeight(Color_Blue, 2)',
                    'ColorWeight(Color_Violet, 0)',
                    'ColorWeight(Color_Orange, 0)',
                ]
            ) + '\n}\n'
            with ZipFile(path, "w") as zf:
                zf.writestr(DEFAULT_LEVELS, props)
                zf.writestr(GLOW_SCD, 'VarFloat("f_pp_glow_factor", 1.0)')
                zf.writestr(GLOW_SCR, 'VarFloat("f_glow_factor", 1.0)')
                zf.writestr(CAR_PHYSICS, 'Ignore(0)\nIgnore(0)\n')
                zf.writestr(OLD_BOAT_PHYSICS, 'Ignore(0)\nIgnore(0)\n')
                zf.writestr(GAME_AUDIO_EFFECTS, '!ReverbPreset(i)\n!ReverbWetDryMix(f)\nReverbPreset(1)\nReverbWetDryMix(0.5)\n')
                zf.writestr(DEFAULT_LOOT, loot)
                zf.writestr(INVENTORY_GEN, 'Weapon("Auto")\n{\nReloadTime(3.0)\n}\n')
                zf.writestr(INVENTORY_SPECIAL, 'Weapon("Fury")\n{\nAimFov(1.0)\n}\n')
                zf.writestr(INTRO_MOVIES, 'PlayMovie("intro")\n')
                for member in CHARACTER_SKILLS.values():
                    zf.writestr(member, skill)
            before = path.read_bytes()
            result = audit_data0(path)
            self.assertEqual(result["sunflare"]["f_glow_factor"], "1.0")
            self.assertEqual(result["deeper_pockets"]["logan"]["inventory_change"], "2")
            self.assertEqual(result["vehicle_noclip"]["car"], {"0": 2})
            self.assertEqual(result["intro"]["statements"][0]["argument"], "intro")
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
