import unittest

from dirue.errors import PatchError
from dirue.structured import (
    replace_call_sequence_in_named_block,
    set_first_quoted_argument_call_commented,
)


class StructuredPatchTests(unittest.TestCase):
    def test_first_quoted_argument_toggle_preserves_later_arguments(self):
        source = '  File("Intro_720p", 0, true);\r\n//File("Other");\r\n'
        disabled = set_first_quoted_argument_call_commented(
            source,
            call_name="File",
            argument="Intro_720p",
            commented=True,
        )
        self.assertEqual(
            disabled,
            '  //File("Intro_720p", 0, true);\r\n//File("Other");\r\n',
        )
        self.assertEqual(
            set_first_quoted_argument_call_commented(
                disabled,
                call_name="File",
                argument="Intro_720p",
                commented=False,
            ),
            source,
        )

    def test_first_quoted_argument_rejects_duplicate_target(self):
        source = 'File("Intro_720p", 0)\nFile("Intro_720p", 1)\n'
        with self.assertRaises(PatchError):
            set_first_quoted_argument_call_commented(
                source,
                call_name="File",
                argument="Intro_720p",
                commented=True,
            )

    def test_named_block_call_sequence_changes_only_target(self):
        source = (
            'ContactParams("Terrain")\n'
            '{\n'
            '    Ignore(0)\n'
            '}\n'
            'ContactParams("SimpleObjects")\n'
            '{\n'
            '    Ignore(0) // target\n'
            '}\n'
        )
        result = replace_call_sequence_in_named_block(
            source,
            block_call="ContactParams",
            block_name="SimpleObjects",
            call_name="Ignore",
            expected_arguments=("0",),
            desired_arguments=("1",),
        )
        self.assertIn('ContactParams("Terrain")\n{\n    Ignore(0)', result)
        self.assertIn('Ignore(1) // target', result)

    def test_named_block_rejects_wrong_prior_sequence(self):
        source = 'Item("Gun")\n{\n    ShotTime(0.6)\n    ShotTime(0.5)\n}\n'
        with self.assertRaises(PatchError):
            replace_call_sequence_in_named_block(
                source,
                block_call="Item",
                block_name="Gun",
                call_name="ShotTime",
                expected_arguments=("0.6", "0.4"),
                desired_arguments=("0.5", "0.3"),
            )

    def test_named_block_brace_scan_ignores_string_and_comment_braces(self):
        source = (
            'Item("Gun")\n'
            '{\n'
            '    Note("}")\n'
            '    // } ignored\n'
            '    ShotTime(0.6)\n'
            '}\n'
            'Item("Other")\n'
            '{\n'
            '    ShotTime(9.9)\n'
            '}\n'
        )
        result = replace_call_sequence_in_named_block(
            source,
            block_call="Item",
            block_name="Gun",
            call_name="ShotTime",
            expected_arguments=("0.6",),
            desired_arguments=("0.5",),
        )
        self.assertIn('ShotTime(0.5)', result)
        self.assertIn('ShotTime(9.9)', result)

    def test_named_block_rejects_duplicate_named_block(self):
        source = 'Item("Gun")\n{\nShotTime(1)\n}\n' * 2
        with self.assertRaises(PatchError):
            replace_call_sequence_in_named_block(
                source,
                block_call="Item",
                block_name="Gun",
                call_name="ShotTime",
                expected_arguments=("1",),
                desired_arguments=("2",),
            )


if __name__ == "__main__":
    unittest.main()
