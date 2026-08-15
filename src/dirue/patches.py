"""Small semantic patch primitives with strict match validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
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


def replace_call_value(
    text: str,
    call_name: str,
    expected_value: str,
    new_value: str,
    *,
    expected_matches: int = 1,
) -> str:
    """Replace a simple `Call(value)` argument with exact match-count validation."""
    pattern = (
        rf'(?P<prefix>\b{re.escape(call_name)}\(\s*)'
        rf'{re.escape(expected_value)}'
        rf'(?P<suffix>\s*\))'
    )
    return apply_regex_patch(
        text,
        RegexPatch(
            name=f"call {call_name}",
            pattern=pattern,
            replacement=rf"\g<prefix>{new_value}\g<suffix>",
            expected_matches=expected_matches,
        ),
    )


def replace_named_call_value(
    text: str,
    call_name: str,
    argument: str,
    expected_value: str,
    new_value: str,
    *,
    expected_matches: int = 1,
) -> str:
    """Replace `Call("name", value)` by call and named-argument identity."""
    pattern = (
        rf'(?P<prefix>\b{re.escape(call_name)}\(\s*"{re.escape(argument)}"\s*,\s*)'
        rf'{re.escape(expected_value)}'
        rf'(?P<suffix>\s*\))'
    )
    return apply_regex_patch(
        text,
        RegexPatch(
            name=f"{call_name} {argument}",
            pattern=pattern,
            replacement=rf"\g<prefix>{new_value}\g<suffix>",
            expected_matches=expected_matches,
        ),
    )


def replace_deeper_pockets_skill(
    text: str,
    *,
    expected_desc_params: str,
    new_desc_params: str,
    expected_inventory_change: str,
    new_inventory_change: str,
) -> str:
    """Update the DeeperPockets skill and its InventorySize effect as one scoped edit."""
    block_pattern = re.compile(
        r'(?P<open><skill\b(?=[^>]*\bid="DeeperPockets")[^>]*>)'
        r'(?P<body>.*?</skill>)',
        re.DOTALL,
    )
    matches = list(block_pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(
            f"DeeperPockets skill: expected 1 match, found {len(matches)}"
        )

    match = matches[0]
    open_tag = match.group("open")
    desc_pattern = re.compile(
        rf'(?P<prefix>\bdesc_params=")'
        rf'{re.escape(expected_desc_params)}'
        rf'(?P<suffix>")'
    )
    new_open, desc_count = desc_pattern.subn(
        rf"\g<prefix>{new_desc_params}\g<suffix>", open_tag
    )
    if desc_count != 1:
        raise PatchError(
            f"DeeperPockets desc_params: expected 1 match, found {desc_count}"
        )

    body = match.group("body")
    effect_pattern = re.compile(
        rf'(?P<prefix><effect\b(?=[^>]*\bid="InventorySize")[^>]*\bchange=")'
        rf'{re.escape(expected_inventory_change)}'
        rf'(?P<suffix>"[^>]*/>)'
    )
    new_body, effect_count = effect_pattern.subn(
        rf"\g<prefix>{new_inventory_change}\g<suffix>", body
    )
    if effect_count != 1:
        raise PatchError(
            f"DeeperPockets InventorySize: expected 1 match, found {effect_count}"
        )

    new_block = new_open + new_body
    return text[: match.start()] + new_block + text[match.end() :]


def _line_parts(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def set_quoted_call_commented(
    text: str,
    *,
    call_name: str,
    argument: str,
    commented: bool,
    expected_matches: int = 1,
) -> str:
    """Comment or uncomment one quoted-argument call without copying its full line."""
    if expected_matches < 1:
        raise PatchError(f"{call_name} {argument}: expected match count must be positive")

    pattern = re.compile(
        rf'^(?P<indent>[ \t]*)(?P<comment>//[ \t]*)?'
        rf'(?P<body>{re.escape(call_name)}\(\s*"{re.escape(argument)}"\s*\)\s*;?)'
        rf'(?P<suffix>[ \t]*(?://.*)?)$'
    )
    states: list[bool] = []
    for line in text.splitlines(keepends=True):
        body, _ = _line_parts(line)
        match = pattern.match(body)
        if match:
            states.append(match.group("comment") is not None)

    if len(states) != expected_matches:
        raise PatchError(
            f"{call_name} {argument}: expected {expected_matches} match(es), found {len(states)}"
        )
    if any(state != states[0] for state in states[1:]):
        raise PatchError(f"{call_name} {argument}: mixed source state")
    if states[0] is commented:
        return text

    updated: list[str] = []
    for line in text.splitlines(keepends=True):
        body, newline = _line_parts(line)
        match = pattern.match(body)
        if not match:
            updated.append(line)
            continue
        marker = "//" if commented else ""
        updated.append(
            f'{match.group("indent")}{marker}{match.group("body")}{match.group("suffix")}{newline}'
        )
    return "".join(updated)


def replace_color_weight_set(
    text: str,
    color_set: str,
    expected_weights: Mapping[str, str],
    new_weights: Mapping[str, str],
) -> str:
    """Replace all weights inside one named `DefColorSet` block."""
    if set(expected_weights) != set(new_weights):
        raise PatchError(f"{color_set}: expected and desired color keys differ")

    block_pattern = re.compile(
        rf'(?P<header>^[ \t]*DefColorSet\(\s*{re.escape(color_set)}\s*\)[ \t]*'
        rf'(?:\r?\n[ \t]*)?\{{[ \t]*\r?$)'
        r'(?P<body>.*?)'
        r'(?P<close>^[ \t]*\}[ \t]*\r?$)',
        re.MULTILINE | re.DOTALL,
    )
    matches = list(block_pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(f"{color_set}: expected 1 block, found {len(matches)}")

    block = matches[0]
    body = block.group("body")
    weight_pattern = re.compile(
        r'^(?![ \t]*//)'
        r'(?P<prefix>[ \t]*ColorWeight\(\s*(?P<color>Color_[A-Za-z]+)\s*,\s*)'
        r'(?P<value>[-+0-9.]+)'
        r'(?P<suffix>\s*\)\s*;?)',
        re.MULTILINE,
    )
    found: dict[str, str] = {}
    for match in weight_pattern.finditer(body):
        color = match.group("color")
        if color in found:
            raise PatchError(f"{color_set}: duplicate {color}")
        found[color] = match.group("value")

    if set(found) != set(expected_weights):
        raise PatchError(
            f"{color_set}: expected colors {sorted(expected_weights)}, found {sorted(found)}"
        )
    for color, value in expected_weights.items():
        if found[color] != value:
            raise PatchError(
                f"{color_set} {color}: expected {value}, found {found[color]}"
            )

    def replace_weight(match: re.Match[str]) -> str:
        return (
            f'{match.group("prefix")}{new_weights[match.group("color")]}''
            f'{match.group("suffix")}'
        )

    new_body, count = weight_pattern.subn(replace_weight, body)
    if count != len(expected_weights):
        raise PatchError(
            f"{color_set}: expected {len(expected_weights)} weights, found {count}"
        )

    new_block = block.group("header") + new_body + block.group("close")
    return text[: block.start()] + new_block + text[block.end() :]


def _reverb_line_state(
    text: str,
    *,
    name: str,
    declaration: bool,
    expected_matches: int,
) -> tuple[list[bool], re.Pattern[str]]:
    if expected_matches < 1:
        raise PatchError(f"{name}: expected match count must be positive")

    escaped = re.escape(name)
    if declaration:
        pattern = re.compile(
            rf"^(?P<indent>[ \t]*)!(?P<comment>//)?(?P<body>{escaped}\([^\r\n]*\))(?P<suffix>[ \t]*(?://.*)?)$"
        )
    else:
        pattern = re.compile(
            rf"^(?P<indent>[ \t]*)(?P<comment>//[ \t]*)?(?P<body>{escaped}\([^\r\n]*\))(?P<suffix>[ \t]*(?://.*)?)$"
        )

    states: list[bool] = []
    for line in text.splitlines(keepends=True):
        body, _ = _line_parts(line)
        match = pattern.match(body)
        if match:
            states.append(match.group("comment") is None)

    if len(states) != expected_matches:
        raise PatchError(
            f"{name}: expected {expected_matches} match(es), found {len(states)}"
        )
    if any(state != states[0] for state in states[1:]):
        raise PatchError(f"{name}: mixed enabled and disabled source state")
    return states, pattern


def _rewrite_reverb_lines(
    text: str,
    pattern: re.Pattern[str],
    *,
    enabled: bool,
    declaration: bool,
) -> str:
    updated: list[str] = []
    for line in text.splitlines(keepends=True):
        body, newline = _line_parts(line)
        match = pattern.match(body)
        if not match:
            updated.append(line)
            continue

        marker = "" if enabled else "//"
        bang = "!" if declaration else ""
        updated.append(
            f'{match.group("indent")}{bang}{marker}{match.group("body")}{match.group("suffix")}{newline}'
        )
    return "".join(updated)


def set_reverb_enabled(
    text: str,
    *,
    enabled: bool,
    expected_preset_calls: int,
    expected_mix_calls: int,
) -> str:
    """Enable or disable the upstream reverb directives without replacing the whole file.

    The expected call counts come from the validated source member. All declarations and
    calls must start in one consistent state; partial or ambiguous input fails closed.
    """
    preset_decl, preset_decl_pattern = _reverb_line_state(
        text,
        name="ReverbPreset",
        declaration=True,
        expected_matches=1,
    )
    mix_decl, mix_decl_pattern = _reverb_line_state(
        text,
        name="ReverbWetDryMix",
        declaration=True,
        expected_matches=1,
    )
    preset_calls, preset_call_pattern = _reverb_line_state(
        text,
        name="ReverbPreset",
        declaration=False,
        expected_matches=expected_preset_calls,
    )
    mix_calls, mix_call_pattern = _reverb_line_state(
        text,
        name="ReverbWetDryMix",
        declaration=False,
        expected_matches=expected_mix_calls,
    )

    states = preset_decl + mix_decl + preset_calls + mix_calls
    if any(state != states[0] for state in states[1:]):
        raise PatchError("reverb: declarations and calls are in mixed source states")
    if states[0] is enabled:
        return text

    updated = _rewrite_reverb_lines(
        text, preset_decl_pattern, enabled=enabled, declaration=True
    )
    updated = _rewrite_reverb_lines(
        updated, mix_decl_pattern, enabled=enabled, declaration=True
    )
    updated = _rewrite_reverb_lines(
        updated, preset_call_pattern, enabled=enabled, declaration=False
    )
    return _rewrite_reverb_lines(
        updated, mix_call_pattern, enabled=enabled, declaration=False
    )
