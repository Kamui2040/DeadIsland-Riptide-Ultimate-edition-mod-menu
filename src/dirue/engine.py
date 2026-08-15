"""Build validated Data0 candidates from ready semantic definitions."""

from __future__ import annotations

import codecs
import copy
from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
import zipfile

from .archive import validate_archive
from .catalog import EXCLUSIVE_PATCH_GROUPS, READY_PATCHES
from .definitions import apply_definition
from .errors import PatchError, ValidationError


@dataclass(frozen=True)
class CandidateBuild:
    source_sha256: str
    candidate_sha256: str
    entry_count: int
    selected_options: tuple[str, ...]
    changed_members: tuple[str, ...]


def _decode_member(data: bytes, member: str) -> tuple[str, bool]:
    had_bom = data.startswith(codecs.BOM_UTF8)
    payload = data[len(codecs.BOM_UTF8) :] if had_bom else data
    try:
        return payload.decode("utf-8"), had_bom
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode patch target {member}") from exc


def _encode_member(text: str, had_bom: bool) -> bytes:
    data = text.encode("utf-8")
    return codecs.BOM_UTF8 + data if had_bom else data


def _ordered_patch_names(selected: tuple[str, ...]) -> tuple[str, ...]:
    """Apply upgrading before camera FOV while preserving all other relative order."""
    ordered = list(selected)
    upgrading = "better_firearm_upgrading"
    camera = {"camera_fov_72", "camera_fov_82"}
    if upgrading not in ordered or not camera.intersection(ordered):
        return tuple(ordered)

    upgrading_index = ordered.index(upgrading)
    first_camera_index = min(
        index for index, name in enumerate(ordered) if name in camera
    )
    if upgrading_index > first_camera_index:
        ordered.pop(upgrading_index)
        ordered.insert(first_camera_index, upgrading)
    return tuple(ordered)


def build_candidate(
    source_archive: Path,
    destination: Path,
    selected_options: tuple[str, ...] | list[str],
) -> CandidateBuild:
    """Build one validated candidate without extracting or changing the source archive."""
    source_archive = Path(source_archive)
    destination = Path(destination)
    source_info = validate_archive(source_archive)

    try:
        same_path = source_archive.resolve() == destination.resolve()
    except FileNotFoundError:
        same_path = False
    if same_path:
        raise ValidationError("candidate destination must differ from source archive")
    if destination.exists():
        raise ValidationError(f"candidate destination already exists: {destination}")

    selected = tuple(selected_options)
    if not selected:
        raise PatchError("no patch options selected")
    if len(selected) != len(set(selected)):
        raise PatchError("duplicate patch option selected")

    unknown = [name for name in selected if name not in READY_PATCHES]
    if unknown:
        raise PatchError("option is not ready for candidate builds: " + ", ".join(unknown))

    selected_set = set(selected)
    for group in EXCLUSIVE_PATCH_GROUPS:
        conflicts = sorted(selected_set & group)
        if len(conflicts) > 1:
            raise PatchError(
                "mutually exclusive patch options selected: " + ", ".join(conflicts)
            )

    required_members = tuple(
        sorted(
            {
                edit.member
                for name in selected
                for edit in READY_PATCHES[name].edits
            }
        )
    )

    original_bytes: dict[str, bytes] = {}
    member_text: dict[str, str] = {}
    member_bom: dict[str, bool] = {}
    with zipfile.ZipFile(source_archive, "r") as source:
        names = set(source.namelist())
        missing = [member for member in required_members if member not in names]
        if missing:
            raise PatchError("missing patch target(s): " + ", ".join(missing))
        for member in required_members:
            data = source.read(member)
            text, had_bom = _decode_member(data, member)
            original_bytes[member] = data
            member_text[member] = text
            member_bom[member] = had_bom

    updated = dict(member_text)
    for name in _ordered_patch_names(selected):
        before = dict(updated)
        updated = apply_definition(updated, READY_PATCHES[name])
        if updated == before:
            raise PatchError(
                f"{name}: made no changes; source may not be a pristine baseline"
            )

    replacements = {
        member: _encode_member(updated[member], member_bom[member])
        for member in required_members
        if updated[member] != member_text[member]
    }
    if not replacements:
        raise PatchError("selected options produced no candidate changes")

    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(source_archive, "r") as source, zipfile.ZipFile(
            temp_path, "w", allowZip64=True
        ) as output:
            for info in source.infolist():
                data = replacements.get(info.filename)
                if data is None:
                    data = source.read(info)
                output.writestr(copy.copy(info), data)

        candidate_info = validate_archive(temp_path)
        if candidate_info.entry_count != source_info.entry_count:
            raise ValidationError("candidate entry count differs from source archive")

        source_after = validate_archive(source_archive)
        if source_after.sha256 != source_info.sha256:
            raise ValidationError("source archive changed while candidate was being built")

        os.replace(temp_path, destination)
        installed_candidate = validate_archive(destination)
        if installed_candidate.sha256 != candidate_info.sha256:
            raise ValidationError("candidate hash changed during final placement")
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise

    changed_members = tuple(sorted(replacements))
    return CandidateBuild(
        source_sha256=source_info.sha256,
        candidate_sha256=installed_candidate.sha256,
        entry_count=installed_candidate.entry_count,
        selected_options=selected,
        changed_members=changed_members,
    )
