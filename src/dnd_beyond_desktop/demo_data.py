from __future__ import annotations

from .models import CharacterSheet, ResourceItem


def load_demo_characters() -> list[CharacterSheet]:
    return [
        CharacterSheet(
            id="arannis-shadowstep",
            name="Arannis Shadowstep",
            class_name="Rogue",
            subclass="Arcane Trickster",
            level=9,
            race="Wood Elf",
            background="Criminal",
            alignment="Chaotic Neutral",
            armor_class=17,
            hit_points=58,
            hit_points_max=58,
            speed=35,
            proficiency_bonus=4,
            abilities={"STR": 10, "DEX": 18, "CON": 14, "INT": 16, "WIS": 12, "CHA": 11},
            skills={
                "Stealth": "+10",
                "Investigation": "+7",
                "Perception": "+4",
                "Sleight of Hand": "+10",
            },
            attacks=["Rapier +10 to hit, 1d8+4 piercing", "Shortbow +10 to hit, 1d6+4 piercing"],
            spell_slots={"1st": 4, "2nd": 2},
            actions=["Cunning Action", "Sneak Attack", "Mage Hand Legerdemain"],
            reactions=["Uncanny Dodge"],
            spells=["Disguise Self", "Mage Hand", "Invisibility"],
            resources=[
                ResourceItem(
                    title="Mage Hand Legerdemain",
                    category="Feature",
                    description="Use Mage Hand to manipulate objects and pockets at range.",
                ),
                ResourceItem(
                    title="Thieves' Tools",
                    category="Tool",
                    description="Advantage on checks to open locks and disarm traps.",
                ),
            ],
            notes="Keep this character ready for quick infiltration notes and trap reminders.",
        ),
        CharacterSheet(
            id="lyra-stormtide",
            name="Lyra Stormtide",
            class_name="Cleric",
            subclass="Tempest Domain",
            level=7,
            race="Half-Elf",
            background="Sailor",
            alignment="Lawful Good",
            armor_class=18,
            hit_points=49,
            hit_points_max=49,
            speed=30,
            proficiency_bonus=3,
            abilities={"STR": 12, "DEX": 10, "CON": 16, "INT": 11, "WIS": 18, "CHA": 14},
            skills={
                "Insight": "+7",
                "Medicine": "+7",
                "Religion": "+4",
                "Athletics": "+3",
            },
            attacks=["Mace +5 to hit, 1d6+1 bludgeoning", "Sacred Flame save DC 15"],
            spell_slots={"1st": 4, "2nd": 3, "3rd": 3},
            actions=["Channel Divinity: Destructive Wrath", "Cast a prepared spell"],
            reactions=["Wrath of the Storm"],
            spells=["Bless", "Healing Word", "Thunderwave", "Guiding Bolt"],
            resources=[
                ResourceItem(
                    title="Channel Divinity",
                    category="Feature",
                    description="Use destructive wrath or turn the tide in combat.",
                ),
                ResourceItem(
                    title="Prepared Spells",
                    category="Spells",
                    description="Quick access to healing and storm-themed support magic.",
                ),
            ],
            notes="Track healing targets, concentration, and emergency spells here.",
        ),
    ]
