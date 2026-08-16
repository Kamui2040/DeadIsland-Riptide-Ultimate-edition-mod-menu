"""User-facing option metadata for the native Linux GUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckboxOption:
    option: str
    label: str
    section: str


@dataclass(frozen=True)
class Choice:
    label: str
    option: str | None = None
    enabled: bool = True
    note: str = ""


@dataclass(frozen=True)
class ChoiceGroup:
    key: str
    label: str
    section: str
    choices: tuple[Choice, ...]


CHECKBOX_OPTIONS = (
    CheckboxOption("reduce_sprint_stamina", "Reduce sprint stamina", "Gameplay"),
    CheckboxOption("reduce_jump_stamina", "Reduce jump stamina", "Gameplay"),
    CheckboxOption("reduce_sunflare", "Reduce sunflare 90%", "Gameplay"),
    CheckboxOption("run_with_weapons", "Run with weapons", "Gameplay"),
    CheckboxOption("better_movement", "Better movement", "Gameplay"),
    CheckboxOption("hold_more_ammo", "Hold more ammo", "Gameplay"),
    CheckboxOption("instant_break_doors", "Instantly break doors", "Gameplay"),
    CheckboxOption("increase_durability", "Increase durability", "Gameplay"),
    CheckboxOption("bullet_penetration", "Bullet penetration", "Gameplay"),
    CheckboxOption("deeper_pockets", "Even deeper pockets", "Gameplay"),
    CheckboxOption("skip_intro_videos", "Skip intro videos", "Gameplay"),
    CheckboxOption("improved_loot", "Improved loot", "Gameplay"),
    CheckboxOption("remove_reverb", "Remove reverb / echo", "Gameplay"),
    CheckboxOption("noclip_vehicles", "NoClip vehicles", "Gameplay"),
    CheckboxOption(
        "better_firearm_upgrading",
        "Better firearms upgrading",
        "Firearms",
    ),
)


CHOICE_GROUPS = (
    ChoiceGroup(
        "ai_difficulty",
        "Zombie difficulty",
        "AI",
        (
            Choice("Normal"),
            Choice("One hit", "one_hit_ai"),
            Choice("Hard", "hard_ai"),
            Choice("Headshot only", "headshot_only_ai"),
        ),
    ),
    ChoiceGroup(
        "firearm_pov",
        "Better firearms POV",
        "Firearms",
        (
            Choice("Off"),
            Choice("FOV 62", "better_firearm_pov_62"),
            Choice("FOV 72", "better_firearm_pov_72"),
            Choice("FOV 82", "better_firearm_pov_82"),
        ),
    ),
    ChoiceGroup(
        "camera_fov",
        "Camera FOV",
        "Camera",
        (
            Choice("Default (62.5)"),
            Choice("72", "camera_fov_72"),
            Choice("82", "camera_fov_82"),
        ),
    ),
    ChoiceGroup(
        "zombie_size",
        "Zombie size",
        "AI",
        (
            Choice("Normal"),
            Choice("Extra small", "zombie_size_extra_small"),
            Choice("Midget", "zombie_size_midget"),
            Choice("Large", "zombie_size_large"),
            Choice("Supersize", "zombie_size_supersize"),
        ),
    ),
    ChoiceGroup(
        "weather_time",
        "Weather / time",
        "World",
        (
            Choice("Default"),
            Choice("Just night", "weather_just_night"),
            Choice("Rain (day)", "weather_rain_day"),
            Choice("Rain (night)", "weather_rain_night"),
            Choice("Storm (day)", "weather_storm_day"),
            Choice("Storm (night)", "weather_storm_night"),
            Choice("Just night (darker)", "weather_just_night_darker"),
            Choice("Rain (darker night)", "weather_rain_night_darker"),
            Choice("Storm (darker night)", "weather_storm_night_darker"),
        ),
    ),
    ChoiceGroup(
        "forced_spawn",
        "Forced spawn",
        "AI",
        (
            Choice("Normal"),
            Choice(
                "Butchers — unavailable",
                enabled=False,
                note="Provenance-safe transform unresolved",
            ),
            Choice(
                "Rams — unavailable",
                enabled=False,
                note="Provenance-safe transform unresolved",
            ),
            Choice(
                "Bloaters — unavailable",
                enabled=False,
                note="Provenance-safe transform unresolved",
            ),
            Choice(
                "Thugs — unavailable",
                enabled=False,
                note="Provenance-safe transform unresolved",
            ),
            Choice("Suiciders", "force_suiciders"),
            Choice("Bandits with guns", "force_bandits_guns"),
            Choice("Bandits with melee", "force_bandits_melee"),
        ),
    ),
)


def ready_ui_options() -> tuple[str, ...]:
    options = [item.option for item in CHECKBOX_OPTIONS]
    options.extend(
        choice.option
        for group in CHOICE_GROUPS
        for choice in group.choices
        if choice.option is not None and choice.enabled
    )
    return tuple(options)
