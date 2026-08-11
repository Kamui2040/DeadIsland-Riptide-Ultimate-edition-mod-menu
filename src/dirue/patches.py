"""Small semantic patch primitives with strict match validation."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .errors import PatchError


@dataclass(frozen=True)
class RegexPatch:
    name: str
    pattern: str
    replacement: str
    expected_matches: int = 1
    flags: int = re.MULTILINE


def apply_regex_patch(text: str, patch: RegexPatch) -> str:
    updated, count = re.subn(patch.pattern, patch.replacement, text, flags=patch.flags)
    if count != patch.expected_matches:
        raise PatchError(
            f"{patch.name}: expected {patch.expected_matches} match(es), found {count}"
        )
    return updated


def replace_xml_prop_value(text: str, prop_name: str, expected_value: str, new_value: str) -> str:
    """Replace one `<prop n="..." v="..."/>` value while preserving surrounding text."""
    pattern = (
        rf'(?P<prefix><prop\s+n="{re.escape(prop_name)}"\s+v=")'
        rf'{re.escape(expected_value)}'
        rf'(?P<suffix>"\s*/>)'
    )
    return apply_regex_patch(
        text,
        RegexPatch(
            name=f"XML property {prop_name}",
            pattern=pattern,
            replacement=rf"\g<prefix>{new_value}\g<suffix>",
        ),
    )


def replace_varfloat_value(text: str, variable_name: str, expected_value: str, new_value: str) -> str:
    """Replace one `VarFloat("name", value)` call by variable identity."""
    pattern = (
        rf'(?P<prefix>VarFloat\(\s*"{re.escape(variable_name)}"\s*,\s*)'
        rf'{re.escape(expected_value)}'
        rf'(?P<suffix>\s*\))'
    )
    return apply_regex_patch(
        text,
        RegexPatch(
            name=f"VarFloat {variable_name}",
            pattern=pattern,
            replacement=rf"\g<prefix>{new_value}\g<suffix>",
        ),
    )
