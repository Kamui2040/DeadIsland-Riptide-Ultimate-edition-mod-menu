import unittest

from dirue.definitions import apply_definition
from dirue.weather import LOGIC_SCRIPT, WEATHER_RAIN_DAY


class WeatherNativeSpacingTests(unittest.TestCase):
    def test_blank_line_between_weather_declarations_is_supported(self):
        native = (
            '\t// WEATHER START ///////////////////////////////////////////\r\n'
            '\textern float f_game_weather;\r\n'
            '\r\n'
            '\textern float f_weather_interior;\r\n'
            '\tfloat interior = clamp(f_weather_interior);\r\n'
            '\tfloat interior_inv = 1.0 - interior;\r\n'
        )

        result = apply_definition(
            {LOGIC_SCRIPT: native},
            WEATHER_RAIN_DAY,
        )[LOGIC_SCRIPT]

        self.assertIn(
            '\textern float f_game_weather;\r\n'
            '\tset("f_game_weather", (0.8));\r\n'
            '\r\n'
            '\textern float f_weather_interior;\r\n',
            result,
        )
        self.assertIn(
            '\tfloat interior_inv = 1.0 - interior;\r\n'
            '\t//set("f_weather_interior", (0.1));\r\n',
            result,
        )
        self.assertEqual(result.count("\n"), result.count("\r\n"))


if __name__ == "__main__":
    unittest.main()
