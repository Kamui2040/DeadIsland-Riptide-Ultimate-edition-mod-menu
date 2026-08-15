"""Structured helpers for semantic firearm item transforms."""

from __future__ import annotations

import re

from .errors import PatchError
from .structured import _first_quoted_argument_block_span


def replace_unique_call_in_first_quoted_block(
    text: str,
    *,
    block_call: str,
    block_name: str,
    expected_call: str,
    expected_argument: str,
    desired_call: str,
    desired_argument: str,
) -> str:
    """Replace one uniquely named active call, including its call type, in an item block."""
    start, end = _first_quoted_argument_block_span(text, block_call, block_name)
    block = text[start:end]
    pattern = re.compile(
        rf'^(?![ \t]*//)(?P<indent>[ \t]*){re.escape(expected_call)}\(\s*'
        rf'(?P<argument>[^\r\n)]*?)\s*\)'
        rf'(?P<suffix>\s*;?[ \t]*(?://.*)?)$',
        re.MULTILINE,
    )
    matches = list(pattern.finditer(block))
    found = tuple(match.group("argument").strip() for match in matches)
    if found != (expected_argument,):
        raise PatchError(
            f"{block_call} {block_name} {expected_call}: "
            f"expected one argument {expected_argument!r}, found {found!r}"
        )

    match = matches[0]
    replacement = (
        f'{match.group("indent")}{desired_call}({desired_argument})'
        f'{match.group("suffix")}'
    )
    new_block = block[: match.start()] + replacement + block[match.end() :]
    return text[:start] + new_block + text[end:]
