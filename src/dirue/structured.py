"""Structured text patch helpers for named DIRDE script blocks."""

from __future__ import annotations

import re

from .errors import PatchError


def _line_parts(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def set_first_quoted_argument_call_commented(
    text: str,
    *,
    call_name: str,
    argument: str,
    commented: bool,
    expected_matches: int = 1,
) -> str:
    """Toggle a call by its first quoted argument while preserving later arguments."""
    if expected_matches < 1:
        raise PatchError(f"{call_name} {argument}: expected match count must be positive")

    pattern = re.compile(
        rf'^(?P<indent>[ \t]*)(?P<comment>//[ \t]*)?'
        rf'(?P<body>{re.escape(call_name)}\(\s*"{re.escape(argument)}"'
        rf'(?P<rest>\s*(?:,[^\r\n)]*)?)\)\s*;?)'
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
            f'{match.group("indent")}{marker}{match.group("body")}'
            f'{match.group("suffix")}{newline}'
        )
    return "".join(updated)


def _matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    line_comment = False
    index = open_index
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if line_comment:
            if char in "\r\n":
                line_comment = False
            index += 1
            continue

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
        elif char == "/" and next_char == "/":
            line_comment = True
            index += 1
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
            if depth < 0:
                break
        index += 1

    raise PatchError("named block has unbalanced braces")


def _named_block_span(text: str, block_call: str, block_name: str) -> tuple[int, int]:
    header_pattern = re.compile(
        rf'^[ \t]*{re.escape(block_call)}\(\s*"{re.escape(block_name)}"\s*\)'
        rf'[ \t]*(?:\r?\n[ \t]*)?\{{',
        re.MULTILINE,
    )
    matches = list(header_pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(
            f'{block_call} {block_name}: expected 1 block, found {len(matches)}'
        )
    match = matches[0]
    open_index = text.find("{", match.start(), match.end())
    if open_index < 0:
        raise PatchError(f"{block_call} {block_name}: opening brace not found")
    close_index = _matching_brace(text, open_index)
    return match.start(), close_index + 1


def replace_call_sequence_in_named_block(
    text: str,
    *,
    block_call: str,
    block_name: str,
    call_name: str,
    expected_arguments: tuple[str, ...],
    desired_arguments: tuple[str, ...],
) -> str:
    """Replace a complete active call sequence inside one uniquely named block."""
    if not expected_arguments:
        raise PatchError(f"{block_call} {block_name} {call_name}: empty expected sequence")
    if len(expected_arguments) != len(desired_arguments):
        raise PatchError(
            f"{block_call} {block_name} {call_name}: expected and desired lengths differ"
        )

    start, end = _named_block_span(text, block_call, block_name)
    block = text[start:end]
    pattern = re.compile(
        rf'^(?![ \t]*//)(?P<prefix>[ \t]*{re.escape(call_name)}\(\s*)'
        rf'(?P<arguments>[^\r\n)]*?)'
        rf'(?P<suffix>\s*\)\s*;?[ \t]*(?://.*)?)$',
        re.MULTILINE,
    )
    matches = list(pattern.finditer(block))
    found = tuple(match.group("arguments").strip() for match in matches)
    if found != expected_arguments:
        raise PatchError(
            f"{block_call} {block_name} {call_name}: "
            f"expected sequence {expected_arguments!r}, found {found!r}"
        )

    position = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal position
        value = desired_arguments[position]
        position += 1
        return f'{match.group("prefix")}{value}{match.group("suffix")}'

    new_block, count = pattern.subn(replacement, block)
    if count != len(expected_arguments):
        raise PatchError(
            f"{block_call} {block_name} {call_name}: expected {len(expected_arguments)} calls, found {count}"
        )
    return text[:start] + new_block + text[end:]


def _first_quoted_argument_block_span(
    text: str,
    block_call: str,
    block_name: str,
) -> tuple[int, int]:
    """Find a unique brace block by the first quoted argument of its header call."""
    header_pattern = re.compile(
        rf'^[ \t]*{re.escape(block_call)}\(\s*"{re.escape(block_name)}"\s*'
        rf'(?:,[^\r\n)]*)?\)[ \t]*(?:\r?\n[ \t]*)?\{{',
        re.MULTILINE,
    )
    matches = list(header_pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(
            f'{block_call} {block_name}: expected 1 first-argument block, found {len(matches)}'
        )
    match = matches[0]
    open_index = text.find("{", match.start(), match.end())
    if open_index < 0:
        raise PatchError(f"{block_call} {block_name}: opening brace not found")
    close_index = _matching_brace(text, open_index)
    return match.start(), close_index + 1


def replace_call_sequence_in_first_quoted_block(
    text: str,
    *,
    block_call: str,
    block_name: str,
    call_name: str,
    expected_arguments: tuple[str, ...],
    desired_arguments: tuple[str, ...],
) -> str:
    """Replace one complete call sequence in a block whose header has extra arguments."""
    if not expected_arguments:
        raise PatchError(f"{block_call} {block_name} {call_name}: empty expected sequence")
    if len(expected_arguments) != len(desired_arguments):
        raise PatchError(
            f"{block_call} {block_name} {call_name}: expected and desired lengths differ"
        )

    start, end = _first_quoted_argument_block_span(text, block_call, block_name)
    block = text[start:end]
    pattern = re.compile(
        rf'^(?![ \t]*//)(?P<prefix>[ \t]*{re.escape(call_name)}\(\s*)'
        rf'(?P<arguments>[^\r\n)]*?)'
        rf'(?P<suffix>\s*\)\s*;?[ \t]*(?://.*)?)$',
        re.MULTILINE,
    )
    matches = list(pattern.finditer(block))
    found = tuple(match.group("arguments").strip() for match in matches)
    if found != expected_arguments:
        raise PatchError(
            f"{block_call} {block_name} {call_name}: "
            f"expected sequence {expected_arguments!r}, found {found!r}"
        )

    position = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal position
        value = desired_arguments[position]
        position += 1
        return f'{match.group("prefix")}{value}{match.group("suffix")}'

    new_block, count = pattern.subn(replacement, block)
    if count != len(expected_arguments):
        raise PatchError(
            f"{block_call} {block_name} {call_name}: expected {len(expected_arguments)} calls, found {count}"
        )
    return text[:start] + new_block + text[end:]


def insert_calls_after_marker_ordinals_in_first_quoted_block(
    text: str,
    *,
    block_call: str,
    block_name: str,
    marker_call: str,
    expected_marker_arguments: tuple[str, ...],
    insertions: tuple[tuple[int, tuple[str, ...]], ...],
) -> str:
    """Insert authored calls into validated marker segments of one named item block."""
    if not expected_marker_arguments:
        raise PatchError(
            f"{block_call} {block_name} {marker_call}: empty expected marker sequence"
        )
    insertion_map = dict(insertions)
    if len(insertion_map) != len(insertions):
        raise PatchError(f"{block_call} {block_name}: duplicate insertion ordinal")
    if not insertion_map:
        raise PatchError(f"{block_call} {block_name}: no insertions requested")
    if any(
        ordinal < 1 or ordinal > len(expected_marker_arguments)
        for ordinal in insertion_map
    ):
        raise PatchError(f"{block_call} {block_name}: insertion ordinal out of range")
    if any(not calls for calls in insertion_map.values()):
        raise PatchError(f"{block_call} {block_name}: empty insertion call set")

    start, end = _first_quoted_argument_block_span(text, block_call, block_name)
    block = text[start:end]
    lines = block.splitlines(keepends=True)
    marker_pattern = re.compile(
        rf'^(?![ \t]*//)(?P<indent>[ \t]*){re.escape(marker_call)}\(\s*'
        rf'(?P<arguments>[^\r\n)]*?)\s*\)\s*;?[ \t]*(?://.*)?$'
    )
    marker_sites: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(lines):
        body, _ = _line_parts(line)
        match = marker_pattern.match(body)
        if match:
            marker_sites.append((index, match))

    found_markers = tuple(
        match.group("arguments").strip() for _, match in marker_sites
    )
    if found_markers != expected_marker_arguments:
        raise PatchError(
            f"{block_call} {block_name} {marker_call}: "
            f"expected sequence {expected_marker_arguments!r}, found {found_markers!r}"
        )

    call_name_pattern = re.compile(r'^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(')
    for ordinal, calls in insertion_map.items():
        marker_index = marker_sites[ordinal - 1][0]
        next_index = (
            marker_sites[ordinal][0]
            if ordinal < len(marker_sites)
            else len(lines)
        )
        requested_names: set[str] = set()
        for call in calls:
            call_match = call_name_pattern.match(call)
            if call_match is None:
                raise PatchError(
                    f"{block_call} {block_name}: invalid insertion call {call!r}"
                )
            requested_names.add(call_match.group("name"))
        for line in lines[marker_index + 1 : next_index]:
            stripped = line.lstrip()
            if stripped.startswith("//"):
                continue
            active = call_name_pattern.match(stripped)
            if active and active.group("name") in requested_names:
                raise PatchError(
                    f"{block_call} {block_name}: "
                    f"{active.group('name')} already present in marker segment {ordinal}"
                )

    output: list[str] = []
    marker_ordinal = 0
    default_newline = "\r\n" if "\r\n" in block else "\n"
    for line in lines:
        output.append(line)
        body, newline = _line_parts(line)
        marker_match = marker_pattern.match(body)
        if marker_match is None:
            continue
        marker_ordinal += 1
        calls = insertion_map.get(marker_ordinal)
        if calls is None:
            continue
        line_end = newline or default_newline
        indent = marker_match.group("indent")
        output.extend(f"{indent}{call}{line_end}" for call in calls)

    new_block = "".join(output)
    return text[:start] + new_block + text[end:]
