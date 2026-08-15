import unittest

from dirue.definitions import apply_definition
from dirue.errors import PatchError
from dirue.weather import (
    AMBIENT_SCRIPT,
    LOGIC_SCRIPT,
    WEATHER_PATCHES,
    WEATHER_SCRIPT,
)


_NATIVE_LOGIC = (
    'import "logic_script_game.scr"\r\n'
    '\r\n'
    'sub main()\r\n'
    '{\r\n'
    '\t// WEATHER START ///////////////////////////////////////////\r\n'
    '\textern float f_game_weather;\r\n'
    '\textern float f_weather_interior;\r\n'
    '\tfloat interior = clamp(f_weather_interior);\r\n'
    '\tfloat interior_inv = 1.0 - interior;\r\n'
    '\tfloat fog_min = 0.2;\r\n'
    '}\r\n'
)

_NATIVE_WEATHER = (
    'sub weather()\r\n'
    '{\r\n'
    '\t//time = TIME * 0.1;\r\n'
    '\t//Set("f_game_time", (time - floor(time)) * 24.0);\r\n'
    '}\r\n'
)

_NATIVE_AMBIENT = (
    'VarFloat("f_engine_envprobe_factor", 1.0)\r\n'
    'VarFloat("f_lighting_indirect_factor", 0.45)\r\n'
)


class WeatherTests(unittest.TestCase):
    def _members(self):
        return {
            LOGIC_SCRIPT: _NATIVE_LOGIC,
            WEATHER_SCRIPT: _NATIVE_WEATHER,
            AMBIENT_SCRIPT: _NATIVE_AMBIENT,
        }

    def test_all_released_non_default_modes_match_audited_statement_shape(self):
        expected = {
            "weather_just_night": (None, "0.3", True, True, "0.01", None),
            "weather_rain_day": ("0.8", "0.1", False, False, None, None),
            "weather_rain_night": ("0.8", "0.3", True, True, "0.01", None),
            "weather_storm_day": ("1.0", "0.1", False, False, None, None),
            "weather_storm_night": ("1.0", "0.3", True, True, "0.01", None),
            "weather_just_night_darker": (None, "1.0", True, True, "0.0099", "0.05"),
            "weather_rain_night_darker": ("0.8", "0.3", False, True, "0.0099", "0.05"),
            "weather_storm_night_darker": ("1.0", "0.3", False, True, "0.0099", "0.05"),
        }
        self.assertEqual(set(WEATHER_PATCHES), set(expected))

        for name, (
            game_weather,
            interior_value,
            interior_active,
            night,
            envprobe,
            indirect,
        ) in expected.items():
            with self.subTest(name=name):
                result = apply_definition(self._members(), WEATHER_PATCHES[name])
                logic = result[LOGIC_SCRIPT]

                if game_weather is None:
                    self.assertNotIn('set("f_game_weather",', logic)
                else:
                    self.assertIn(
                        f'set("f_game_weather", ({game_weather}));',
                        logic,
                    )

                interior = f'set("f_weather_interior", ({interior_value}));'
                if interior_active:
                    self.assertIn("\t" + interior, logic)
                    self.assertNotIn("\t//" + interior, logic)
                else:
                    self.assertIn("\t//" + interior, logic)

                weather = result[WEATHER_SCRIPT]
                if night:
                    self.assertIn("\ttime = TIME * 0.0;", weather)
                    self.assertIn(
                        '\tSet("f_game_time", (time - floor(time)) * 8.0);',
                        weather,
                    )
                    self.assertNotIn("//time = TIME * 0.1;", weather)
                else:
                    self.assertEqual(weather, _NATIVE_WEATHER)

                ambient = result[AMBIENT_SCRIPT]
                if envprobe is None:
                    self.assertEqual(ambient, _NATIVE_AMBIENT)
                else:
                    self.assertIn(
                        f'VarFloat("f_engine_envprobe_factor", {envprobe})',
                        ambient,
                    )
                if indirect is not None:
                    self.assertIn(
                        f'VarFloat("f_lighting_indirect_factor", {indirect})',
                        ambient,
                    )

                for member in result.values():
                    self.assertEqual(member.count("\n"), member.count("\r\n"))

    def test_existing_weather_override_fails_closed(self):
        members = self._members()
        members[LOGIC_SCRIPT] = members[LOGIC_SCRIPT].replace(
            '\textern float f_weather_interior;\r\n',
            '\tset("f_game_weather", (0.8));\r\n'
            '\textern float f_weather_interior;\r\n',
        )
        with self.assertRaises(PatchError):
            apply_definition(members, WEATHER_PATCHES["weather_rain_day"])

    def test_wrong_native_time_prior_fails_closed(self):
        members = self._members()
        members[WEATHER_SCRIPT] = members[WEATHER_SCRIPT].replace(
            "TIME * 0.1",
            "TIME * 0.2",
        )
        with self.assertRaises(PatchError):
            apply_definition(members, WEATHER_PATCHES["weather_just_night"])

    def test_missing_semantic_logic_anchor_fails_closed(self):
        members = self._members()
        members[LOGIC_SCRIPT] = members[LOGIC_SCRIPT].replace(
            "// WEATHER START ///////////////////////////////////////////",
            "// OTHER SECTION",
        )
        with self.assertRaises(PatchError):
            apply_definition(members, WEATHER_PATCHES["weather_storm_day"])


if __name__ == "__main__":
    unittest.main()
