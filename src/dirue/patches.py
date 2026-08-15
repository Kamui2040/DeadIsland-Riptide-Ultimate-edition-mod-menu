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


def _line_parts(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


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
