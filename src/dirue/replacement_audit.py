"""Sanitized read-only audit for upstream unconditional replacement files."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root

GAME_INI_MEMBER = "data/game.ini"
MENU_MEMBER = "data/menu/scr/menumain_pc.xui"
GAME_INI_REPLACEMENT = "game.ini"
MENU_REPLACEMENT = "menumain_pc.xui_version"

_CALL_RE = re.compile(
    r"^[ \t]*(?P<comment>//[ \t]*)?"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"\((?P<args>.*)\)[ \t]*;?[ \t]*\r?$",
    re.MULTILINE,
)


def _digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _decode(data: bytes, identity: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode replacement audit target: {identity}") from exc


def _read_member(archive: ZipFile, member: str) -> bytes:
    if member not in archive.namelist():
        raise ValidationError(f"replacement audit missing native member: {member}")
    return archive.read(member)


def _read_replacement(path: Path, identity: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ValidationError(f"cannot read replacement audit input: {identity}") from exc


def _call_summary(text: str) -> list[dict[str, str]]:
    counts: dict[str, int] = {}
    result: list[dict[str, str]] = []
    for match in _CALL_RE.finditer(text):
        name = match.group("name")
        counts[name] = counts.get(name, 0) + 1
        result.append(
            {
                "identity": f"{name}#{counts[name]}",
                "name": name,
                "state": "commented" if match.group("comment") else "active",
                "args_sha256": _digest_text(match.group("args").strip()),
            }
        )
    return result


def game_ini_summary(native: bytes, replacement: bytes) -> dict[str, object]:
    native_calls = _call_summary(_decode(native, GAME_INI_MEMBER))
    replacement_calls = _call_summary(_decode(replacement, GAME_INI_REPLACEMENT))

    native_map = {item["identity"]: item for item in native_calls}
    replacement_map = {item["identity"]: item for item in replacement_calls}

    changed: list[dict[str, str]] = []
    for identity in sorted(native_map.keys() & replacement_map.keys()):
        before = native_map[identity]
        after = replacement_map[identity]
        if before["state"] != after["state"] or before["args_sha256"] != after["args_sha256"]:
            changed.append(
                {
                    "identity": identity,
                    "name": before["name"],
                    "native_state": before["state"],
                    "replacement_state": after["state"],
                    "native_args_sha256": before["args_sha256"],
                    "replacement_args_sha256": after["args_sha256"],
                }
            )

    return {
        "native_sha256": _digest_bytes(native),
        "replacement_sha256": _digest_bytes(replacement),
        "native_call_count": len(native_calls),
        "replacement_call_count": len(replacement_calls),
        "changed_calls": changed,
        "native_only_call_identities": sorted(native_map.keys() - replacement_map.keys()),
        "replacement_only_call_identities": sorted(
            replacement_map.keys() - native_map.keys()
        ),
    }


def _component_identity(element: ET.Element) -> str | None:
    properties = element.find("Properties")
    if properties is None:
        return None
    id_node = properties.find("Id")
    if id_node is None or not (id_node.text or "").strip():
        return None
    return f"{element.tag}:{(id_node.text or '').strip()}"


def _component_map(root: ET.Element) -> dict[str, ET.Element]:
    result: dict[str, ET.Element] = {}
    for element in root.iter():
        identity = _component_identity(element)
        if identity is None:
            continue
        if identity in result:
            raise ValidationError(f"duplicate XUI component identity: {identity}")
        result[identity] = element
    return result


def _property_map(element: ET.Element) -> dict[str, str]:
    properties = element.find("Properties")
    if properties is None:
        return {}
    counts: dict[str, int] = {}
    result: dict[str, str] = {}
    for child in list(properties):
        counts[child.tag] = counts.get(child.tag, 0) + 1
        identity = f"{child.tag}#{counts[child.tag]}"
        result[identity] = _digest_text((child.text or "").strip())
    return result


def _canonical_tuple(element: ET.Element) -> tuple[object, ...]:
    text = (element.text or "").strip()
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        text,
        tuple(_canonical_tuple(child) for child in list(element)),
    )


def _canonical_digest(element: ET.Element) -> str:
    return _digest_text(repr(_canonical_tuple(element)))


def _remove_components(root: ET.Element, identities: set[str]) -> None:
    for parent in root.iter():
        for child in list(parent):
            identity = _component_identity(child)
            if identity in identities:
                parent.remove(child)


def menu_summary(native: bytes, replacement: bytes) -> dict[str, object]:
    try:
        native_root = ET.fromstring(_decode(native, MENU_MEMBER))
        replacement_root = ET.fromstring(
            _decode(replacement, MENU_REPLACEMENT)
        )
    except ET.ParseError as exc:
        raise ValidationError("cannot parse XUI replacement audit input") from exc

    native_components = _component_map(native_root)
    replacement_components = _component_map(replacement_root)

    native_only = set(native_components) - set(replacement_components)
    replacement_only = set(replacement_components) - set(native_components)

    changed_components: list[dict[str, object]] = []
    for identity in sorted(set(native_components) & set(replacement_components)):
        before = native_components[identity]
        after = replacement_components[identity]
        if _canonical_digest(before) == _canonical_digest(after):
            continue
        before_props = _property_map(before)
        after_props = _property_map(after)
        changed_properties: list[dict[str, str]] = []
        for prop in sorted(before_props.keys() | after_props.keys()):
            before_digest = before_props.get(prop)
            after_digest = after_props.get(prop)
            if before_digest == after_digest:
                continue
            changed_properties.append(
                {
                    "property": prop,
                    "native_sha256": before_digest or "missing",
                    "replacement_sha256": after_digest or "missing",
                }
            )
        changed_components.append(
            {
                "identity": identity,
                "changed_properties": changed_properties,
                "native_component_sha256": _canonical_digest(before),
                "replacement_component_sha256": _canonical_digest(after),
            }
        )

    stripped_replacement = deepcopy(replacement_root)
    _remove_components(stripped_replacement, replacement_only)

    return {
        "native_sha256": _digest_bytes(native),
        "replacement_sha256": _digest_bytes(replacement),
        "native_component_count": len(native_components),
        "replacement_component_count": len(replacement_components),
        "native_only_components": sorted(native_only),
        "replacement_only_components": sorted(replacement_only),
        "changed_components": changed_components,
        "equivalent_after_removing_replacement_only_components": (
            _canonical_digest(native_root) == _canonical_digest(stripped_replacement)
        ),
    }


def audit_replacements(root: Path, replacement_dir: Path) -> dict[str, object]:
    """Compare native members to inherited replacements without emitting raw values."""
    game = validate_game_root(root)
    replacement_dir = Path(replacement_dir)

    with ZipFile(game.data0) as archive:
        native_game_ini = _read_member(archive, GAME_INI_MEMBER)
        native_menu = _read_member(archive, MENU_MEMBER)

    replacement_game_ini = _read_replacement(
        replacement_dir / GAME_INI_REPLACEMENT,
        GAME_INI_REPLACEMENT,
    )
    replacement_menu = _read_replacement(
        replacement_dir / MENU_REPLACEMENT,
        MENU_REPLACEMENT,
    )

    return {
        "archive_sha256": game.archive.sha256,
        "game_ini": game_ini_summary(native_game_ini, replacement_game_ini),
        "menumain_pc_xui": menu_summary(native_menu, replacement_menu),
    }
