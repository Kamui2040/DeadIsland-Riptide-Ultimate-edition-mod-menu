import unittest

from dirue.errors import ValidationError
from dirue.weather_probe import (
    _call_argument_states,
    _spawn_vector_digest,
    statement_summary,
)


class WeatherProbeTests(unittest.TestCase):
    def test_statement_summary_handles_nested_calls_comments_and_crlf(self):
        logic = (
            'set("f_game_weather", GetWeather("rain", 1)); // active\r\n'
            '// set("f_weather_interior", false); // intentionally off\r\n'
        )
        weather = (
            '// float time = 22.5; // night\r\n'
            '// Set("f_game_time", GetTime(time, 0)); // night\r\n'
        )
        summary = statement_summary(logic, weather)
        self.assertEqual(
            summary["logic_script"]["f_game_weather"],
            {"active": [['GetWeather("rain", 1)']], "commented": []},
        )
        self.assertEqual(
            summary["logic_script"]["f_weather_interior"],
            {"active": [], "commented": [["false"]]},
        )
        self.assertEqual(
            summary["weather_script"]["time"],
            {"active": [], "commented": ["22.5"]},
        )
        self.assertEqual(
            summary["weather_script"]["f_game_time"],
            {"active": [], "commented": [["GetTime(time, 0)"]]},
        )

    def test_duplicate_recognized_site_fails_closed(self):
        with self.assertRaises(ValidationError):
            _call_argument_states(
                'set("f_game_weather", 1)\nset("f_game_weather", 2)\n',
                "set",
                "f_game_weather",
            )

    def test_spawn_vector_digest_is_order_sensitive_without_exposing_values(self):
        first = _spawn_vector_digest(("alpha", "beta"))
        second = _spawn_vector_digest(("beta", "alpha"))
        self.assertEqual(len(first), 64)
        self.assertNotEqual(first, second)
        self.assertNotIn("alpha", first)
        self.assertNotIn("beta", first)


if __name__ == "__main__":
    unittest.main()
