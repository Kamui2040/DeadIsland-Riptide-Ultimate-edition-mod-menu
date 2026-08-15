"""Semantic weather/time transforms reconstructed from released preset behavior."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .definitions import PatchDefinition, VarFloatEdit
from .errors import PatchError


LOGIC_SCRIPT = "data/scripts/logic_script.scr"
WEATHER_SCRIPT = "data/scripts/weather/weather.scr"
AMBIENT_SCRIPT = "data/scripts/varlist_ambient.scr"


def _single_match(pattern: re.Pattern[str], text: str, identity: str) -> re.Match[str]:
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(f"{identity}: expected exactly one semantic anchor, found {len(matches)}")
    return matches[0]


def _ensure_no_weather_override(text: str, identity: str) -> None:
    pattern = re.compile(
        rf'^[ \t]*(?://[ \t]*)?set\([ \t]*"{re.escape(identity)}"[ \t]*,',
        re.MULTILINE,
    )
    if pattern.search(text):
        raise PatchError(f"weather: unexpected existing {identity} override")


@dataclass(frozen=True)
class WeatherLogicEdit:
    """Insert released weather/interior overrides at stable semantic anchors."""

    member: str
    game_weather: str | None
    interior_value: str
    interior_active: bool

    def apply(self, text: str) -> str:
        _ensure_no_weather_override(text, "f_game_weather")
        _ensure_no_weather_override(text, "f_weather_interior")

        weather_anchor = re.compile(
            r'^(?P<header_indent>[ \t]*)//[ \t]*WEATHER START[^\r\n]*(?P<header_eol>\r?\n)'
            r'(?P<game_line>(?P<game_indent>[ \t]*)extern[ \t]+float[ \t]+'
            r'f_game_weather[ \t]*;[ \t]*(?P<game_eol>\r?\n))'
            r'(?=[ \t]*extern[ \t]+float[ \t]+f_weather_interior[ \t]*;)',
            re.MULTILINE,
        )
        weather_match = _single_match(weather_anchor, text, "weather:f_game_weather")

        interior_anchor = re.compile(
            r'^(?P<indent>[ \t]*)extern[ \t]+float[ \t]+f_weather_interior[ \t]*;'
            r'[ \t]*(?P<eol>\r?\n)'
            r'(?P=indent)float[ \t]+interior[ \t]*=[ \t]*clamp\(f_weather_interior\)'
            r'[ \t]*;[ \t]*(?P=eol)'
            r'(?P<last>(?P=indent)float[ \t]+interior_inv[ \t]*=[ \t]*1\.0'
            r'[ \t]*-[ \t]*interior[ \t]*;[ \t]*(?P=eol))',
            re.MULTILINE,
        )
        interior_match = _single_match(
            interior_anchor,
            text,
            "weather:f_weather_interior",
        )
        if interior_match.start() <= weather_match.start():
            raise PatchError("weather: semantic anchors are in an unexpected order")

        insertions: list[tuple[int, str]] = []
        if self.game_weather is not None:
            insertions.append(
                (
                    weather_match.end("game_line"),
                    (
                        f'{weather_match.group("game_indent")}set('
                        f'"f_game_weather", ({self.game_weather}));'
                        f'{weather_match.group("game_eol")}'
                    ),
                )
            )

        comment = "" if self.interior_active else "//"
        insertions.append(
            (
                interior_match.end("last"),
                (
                    f'{interior_match.group("indent")}{comment}set('
                    f'"f_weather_interior", ({self.interior_value}));'
                    f'{interior_match.group("eol")}'
                ),
            )
        )

        updated = text
        for position, addition in sorted(insertions, reverse=True):
            updated = updated[:position] + addition + updated[position:]
        return updated


@dataclass(frozen=True)
class WeatherTimeEdit:
    """Activate the two native-commented night-time statements with released values."""

    member: str

    def apply(self, text: str) -> str:
        active_time = re.compile(
            r'^(?![ \t]*//)[ \t]*time[ \t]*=',
            re.MULTILINE,
        )
        active_game_time = re.compile(
            r'^(?![ \t]*//)[ \t]*Set\([ \t]*"f_game_time"[ \t]*,',
            re.MULTILINE,
        )
        if active_time.search(text) or active_game_time.search(text):
            raise PatchError("weather: night-time statements are already active")

        time_comment = re.compile(
            r'^(?P<indent>[ \t]*)//[ \t]*time[ \t]*=[ \t]*TIME[ \t]*\*[ \t]*'
            r'0\.1[ \t]*;?[ \t]*(?P<eol>\r?\n|$)',
            re.MULTILINE,
        )
        game_time_comment = re.compile(
            r'^(?P<indent>[ \t]*)//[ \t]*Set\([ \t]*"f_game_time"[ \t]*,'
            r'[ \t]*\(time[ \t]*-[ \t]*floor\(time\)\)[ \t]*\*[ \t]*24\.0'
            r'[ \t]*\)[ \t]*;?[ \t]*(?P<eol>\r?\n|$)',
            re.MULTILINE,
        )

        time_match = _single_match(time_comment, text, "weather:commented time")
        game_time_match = _single_match(
            game_time_comment,
            text,
            "weather:commented f_game_time",
        )

        replacements = (
            (
                time_match.start(),
                time_match.end(),
                f'{time_match.group("indent")}time = TIME * 0.0;{time_match.group("eol")}',
            ),
            (
                game_time_match.start(),
                game_time_match.end(),
                (
                    f'{game_time_match.group("indent")}Set('
                    '"f_game_time", (time - floor(time)) * 8.0);'
                    f'{game_time_match.group("eol")}'
                ),
            ),
        )

        updated = text
        for start, end, replacement in sorted(replacements, reverse=True):
            updated = updated[:start] + replacement + updated[end:]
        return updated


def _weather_definition(
    name: str,
    *,
    game_weather: str | None,
    interior_value: str,
    interior_active: bool,
    night: bool,
    darker: bool = False,
) -> PatchDefinition:
    edits: list[object] = [
        WeatherLogicEdit(
            LOGIC_SCRIPT,
            game_weather,
            interior_value,
            interior_active,
        )
    ]
    if night:
        edits.append(WeatherTimeEdit(WEATHER_SCRIPT))
        edits.append(
            VarFloatEdit(
                AMBIENT_SCRIPT,
                "f_engine_envprobe_factor",
                "1.0",
                "0.0099" if darker else "0.01",
            )
        )
        if darker:
            edits.append(
                VarFloatEdit(
                    AMBIENT_SCRIPT,
                    "f_lighting_indirect_factor",
                    "0.45",
                    "0.05",
                )
            )
    return PatchDefinition(name, tuple(edits))  # type: ignore[arg-type]


WEATHER_JUST_NIGHT = _weather_definition(
    "weather_just_night",
    game_weather=None,
    interior_value="0.3",
    interior_active=True,
    night=True,
)
WEATHER_RAIN_DAY = _weather_definition(
    "weather_rain_day",
    game_weather="0.8",
    interior_value="0.1",
    interior_active=False,
    night=False,
)
WEATHER_RAIN_NIGHT = _weather_definition(
    "weather_rain_night",
    game_weather="0.8",
    interior_value="0.3",
    interior_active=True,
    night=True,
)
WEATHER_STORM_DAY = _weather_definition(
    "weather_storm_day",
    game_weather="1.0",
    interior_value="0.1",
    interior_active=False,
    night=False,
)
WEATHER_STORM_NIGHT = _weather_definition(
    "weather_storm_night",
    game_weather="1.0",
    interior_value="0.3",
    interior_active=True,
    night=True,
)
WEATHER_JUST_NIGHT_DARKER = _weather_definition(
    "weather_just_night_darker",
    game_weather=None,
    interior_value="1.0",
    interior_active=True,
    night=True,
    darker=True,
)
WEATHER_RAIN_NIGHT_DARKER = _weather_definition(
    "weather_rain_night_darker",
    game_weather="0.8",
    interior_value="0.3",
    interior_active=False,
    night=True,
    darker=True,
)
WEATHER_STORM_NIGHT_DARKER = _weather_definition(
    "weather_storm_night_darker",
    game_weather="1.0",
    interior_value="0.3",
    interior_active=False,
    night=True,
    darker=True,
)

WEATHER_PATCHES = {
    definition.name: definition
    for definition in (
        WEATHER_JUST_NIGHT,
        WEATHER_RAIN_DAY,
        WEATHER_RAIN_NIGHT,
        WEATHER_STORM_DAY,
        WEATHER_STORM_NIGHT,
        WEATHER_JUST_NIGHT_DARKER,
        WEATHER_RAIN_NIGHT_DARKER,
        WEATHER_STORM_NIGHT_DARKER,
    )
}
