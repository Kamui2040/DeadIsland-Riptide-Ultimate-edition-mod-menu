import unittest

from dirue.errors import ValidationError
from dirue.unresolved_detail import (
    global_exact_donor_locations,
    weather_constant_summary,
)


class UnresolvedDetailTests(unittest.TestCase):
    def test_weather_summary_reports_only_whitelisted_constants_and_comment_state(self):
        logic = (
            'set("f_game_weather", "Rain");\r\n'
            '// set("f_weather_interior", 0.25);\r\n'
            'set("unrelated", "secret");\r\n'
        )
        weather = (
            '//time = 18.0;\r\n'
            '//Set("f_game_time", 18.0);\r\n'
            'Set("other_time", 99);\r\n'
        )
        ambient = (
            'VarFloat("f_engine_envprobe_factor", 0.01)\r\n'
            'VarFloat("f_lighting_indirect_factor", 0.45)\r\n'
            'VarFloat("other", 123)\r\n'
        )
        result = weather_constant_summary(logic, weather, ambient)
        self.assertEqual(
            result["logic_script"]["f_game_weather"]["active"],
            ['"Rain"'],
        )
        self.assertEqual(
            result["logic_script"]["f_weather_interior"]["commented"],
            ["0.25"],
        )
        self.assertEqual(result["weather_script"]["time"]["commented"], ["18.0"])
        self.assertEqual(
            result["weather_script"]["f_game_time"]["commented"],
            ["18.0"],
        )
        self.assertEqual(
            result["ambient_script"]["f_engine_envprobe_factor"]["active"],
            ["0.01"],
        )
        self.assertNotIn("unrelated", str(result))
        self.assertNotIn("secret", str(result))
        self.assertNotIn("other_time", str(result))

    def test_weather_summary_rejects_ambiguous_recognized_site(self):
        logic = (
            'set("f_game_weather", "Rain");\n'
            'set("f_game_weather", "Storm");\n'
        )
        with self.assertRaises(ValidationError):
            weather_constant_summary(logic, "", "")

    def test_global_donor_search_requires_exact_quoted_value(self):
        result = global_exact_donor_locations(
            {
                "data/a.scr": b'Value("ABC") Value("XABCY")',
                "data/b.scr": b'"ABC" "ABC"',
                "data/c.bin": b'ABC',
            },
            ["ABC", "MISSING"],
        )
        abc = "b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78"
        missing = "8af1d328d75e91cf5fff2deab39607be475491d16c45e89a2721eb14bb9a701e"
        self.assertEqual(
            result[abc],
            [
                {"member": "data/a.scr", "occurrences": 1},
                {"member": "data/b.scr", "occurrences": 2},
            ],
        )
        self.assertEqual(result[missing], [])
        self.assertNotIn("ABC", str(result))
        self.assertNotIn("MISSING", str(result))


if __name__ == "__main__":
    unittest.main()
