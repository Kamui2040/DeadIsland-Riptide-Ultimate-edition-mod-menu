"""User-facing option metadata for the Linux GUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckboxOption:
    option: str
    label: str
    section: str
    theme: str
    help_text: str


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
    help_text: str
    choices: tuple[Choice, ...]


CHECKBOX_OPTIONS = (
    CheckboxOption(
        "reduce_sprint_stamina",
        "Reduce sprint stamina",
        "Gameplay",
        "Movement",
        "Sprint uses much less stamina.",
    ),
    CheckboxOption(
        "reduce_jump_stamina",
        "Reduce jump stamina",
        "Gameplay",
        "Movement",
        "Jumping uses much less stamina.",
    ),
    CheckboxOption(
        "run_with_weapons",
        "Run with weapons",
        "Gameplay",
        "Movement",
        "Lets you sprint while holding weapons.",
    ),
    CheckboxOption(
        "better_movement",
        "Better movement",
        "Gameplay",
        "Movement",
        "Makes movement feel quicker and less restricted.",
    ),
    CheckboxOption(
        "bullet_penetration",
        "Bullet penetration",
        "Gameplay",
        "Combat",
        "Bullets can pass through more targets.",
    ),
    CheckboxOption(
        "instant_break_doors",
        "Instantly break doors",
        "Gameplay",
        "Combat",
        "Breaks kickable doors much faster.",
    ),
    CheckboxOption(
        "increase_durability",
        "Increase durability",
        "Gameplay",
        "Gear & loot",
        "Weapons last longer before they need repairs.",
    ),
    CheckboxOption(
        "hold_more_ammo",
        "Hold more ammo",
        "Gameplay",
        "Gear & loot",
        "Raises the amount of ammo you can carry.",
    ),
    CheckboxOption(
        "deeper_pockets",
        "Even deeper pockets",
        "Gameplay",
        "Gear & loot",
        "Gives you more inventory space.",
    ),
    CheckboxOption(
        "improved_loot",
        "Improved loot",
        "Gameplay",
        "Gear & loot",
        "Improves the quality of loot you find.",
    ),
    CheckboxOption(
        "reduce_sunflare",
        "Reduce sunflare 90%",
        "Gameplay",
        "Comfort",
        "Makes bright sun glare much weaker.",
    ),
    CheckboxOption(
        "remove_reverb_echo",
        "Remove reverb / echo",
        "Gameplay",
        "Comfort",
        "Reduces the strong echo effect in some areas.",
    ),
    CheckboxOption(
        "skip_intro_videos",
        "Skip intro videos",
        "Gameplay",
        "Comfort",
        "Skips the startup logo videos.",
    ),
    CheckboxOption(
        "noclip_vehicles",
        "NoClip vehicles",
        "Gameplay",
        "Vehicles",
        "Lets vehicles pass through some collision. This can get you stuck.",
    ),
    CheckboxOption(
        "better_firearm_upgrading",
        "Better firearms upgrading",
        "Firearms",
        "Firearms",
        "Makes firearm upgrades more useful.",
    ),
)


CHOICE_GROUPS = (
    ChoiceGroup(
        "ai_difficulty",
        "Zombie difficulty",
        "AI",
        "Changes how hard zombies are to kill.",
        (
            Choice("Normal", note="Uses the normal zombie difficulty."),
            Choice("One hit", "one_hit_ai", note="Most zombies die from one hit."),
            Choice("Hard", "hard_ai", note="Makes zombies harder to kill."),
            Choice(
                "Headshot only",
                "headshot_only_ai",
                note="Zombies can only be killed with headshots.",
            ),
        ),
    ),
    ChoiceGroup(
        "zombie_size",
        "Zombie size",
        "AI",
        "Changes the size of spawned zombies.",
        (
            Choice("Normal", note="Keeps normal zombie sizes."),
            Choice("Extra small", "zombie_size_extra_small", note="Makes zombies very small."),
            Choice("Midget", "zombie_size_midget", note="Makes zombies smaller than normal."),
            Choice("Large", "zombie_size_large", note="Makes zombies larger than normal."),
            Choice("Supersize", "zombie_size_supersize", note="Makes zombies very large."),
        ),
    ),
    ChoiceGroup(
        "forced_spawn",
        "Forced spawn",
        "AI",
        "Replaces normal spawns with the selected enemy type.",
        (
            Choice("Normal", note="Uses the normal enemy mix."),
            Choice("Butchers", "force_butchers", note="Forces Butcher spawns."),
            Choice("Rams", "force_rams", note="Forces Ram spawns."),
            Choice("Bloaters", "force_bloaters", note="Forces Bloater spawns."),
            Choice("Thugs", "force_thugs", note="Forces Thug spawns."),
            Choice("Suiciders", "force_suiciders", note="Forces Suicider spawns."),
            Choice(
                "Bandits with guns",
                "force_bandits_guns",
                note="Forces armed Bandit spawns.",
            ),
            Choice(
                "Bandits with melee",
                "force_bandits_melee",
                note="Forces melee Bandit spawns.",
            ),
        ),
    ),
    ChoiceGroup(
        "firearm_pov",
        "Firearms POV",
        "Firearms",
        "Changes how far held firearms sit from the camera.",
        (
            Choice("Off", note="Uses the normal firearm view."),
            Choice("FOV 62", "better_firearm_pov_62", note="Uses the 62 firearm view."),
            Choice("FOV 72", "better_firearm_pov_72", note="Uses the 72 firearm view."),
            Choice("FOV 82", "better_firearm_pov_82", note="Uses the 82 firearm view."),
        ),
    ),
    ChoiceGroup(
        "camera_fov",
        "Camera FOV",
        "Camera",
        "Changes how wide the main camera view is.",
        (
            Choice("Default (62.5)", note="Uses the normal camera view."),
            Choice("72", "camera_fov_72", note="Uses a wider 72 FOV."),
            Choice("82", "camera_fov_82", note="Uses a wider 82 FOV."),
        ),
    ),
    ChoiceGroup(
        "weather_time",
        "Weather / time",
        "World",
        "Locks the world to the selected weather and time setup.",
        (
            Choice("Default", note="Uses the normal weather and time cycle."),
            Choice("Just night", "weather_just_night", note="Keeps the world at night."),
            Choice("Rain (day)", "weather_rain_day", note="Keeps rainy daytime weather."),
            Choice("Rain (night)", "weather_rain_night", note="Keeps rainy nighttime weather."),
            Choice("Storm (day)", "weather_storm_day", note="Keeps stormy daytime weather."),
            Choice("Storm (night)", "weather_storm_night", note="Keeps stormy nighttime weather."),
            Choice(
                "Just night (darker)",
                "weather_just_night_darker",
                note="Keeps the world at a darker night setting.",
            ),
            Choice(
                "Rain (darker night)",
                "weather_rain_night_darker",
                note="Keeps rainy weather with a darker night.",
            ),
            Choice(
                "Storm (darker night)",
                "weather_storm_night_darker",
                note="Keeps stormy weather with a darker night.",
            ),
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
