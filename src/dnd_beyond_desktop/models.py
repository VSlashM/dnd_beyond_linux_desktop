from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class ResourceItem:
    title: str
    category: str
    description: str
    source: str = "D&D Beyond"

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ResourceItem":
        return cls(
            title=str(payload.get("title", "")),
            category=str(payload.get("category", "General")),
            description=str(payload.get("description", "")),
            source=str(payload.get("source", "D&D Beyond")),
        )


@dataclass(slots=True)
class CharacterSheet:
    id: str
    name: str
    class_name: str
    subclass: str
    level: int
    race: str
    background: str
    alignment: str
    armor_class: int
    hit_points: int
    hit_points_max: int
    speed: int
    proficiency_bonus: int
    abilities: dict[str, int] = field(default_factory=dict)
    skills: dict[str, str] = field(default_factory=dict)
    attacks: list[str] = field(default_factory=list)
    spell_slots: dict[str, int] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)
    reactions: list[str] = field(default_factory=list)
    spells: list[str] = field(default_factory=list)
    resources: list[ResourceItem] = field(default_factory=list)
    notes: str = ""
    last_synced: str | None = None
    source: str = "cached"

    def headline(self) -> str:
        subclass = f" ({self.subclass})" if self.subclass else ""
        return f"Level {self.level} {self.class_name}{subclass}"

    def search_blob(self) -> str:
        parts = [
            self.name,
            self.class_name,
            self.subclass,
            self.race,
            self.background,
            self.alignment,
            self.notes,
            " ".join(self.actions),
            " ".join(self.reactions),
            " ".join(self.spells),
            " ".join(self.attacks),
            " ".join(self.skills.keys()),
            " ".join(self.resources[i].title for i in range(len(self.resources))),
        ]
        return " ".join(parts).lower()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "class_name": self.class_name,
            "subclass": self.subclass,
            "level": self.level,
            "race": self.race,
            "background": self.background,
            "alignment": self.alignment,
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "hit_points_max": self.hit_points_max,
            "speed": self.speed,
            "proficiency_bonus": self.proficiency_bonus,
            "abilities": self.abilities,
            "skills": self.skills,
            "attacks": self.attacks,
            "spell_slots": self.spell_slots,
            "actions": self.actions,
            "reactions": self.reactions,
            "spells": self.spells,
            "resources": [resource.to_dict() for resource in self.resources],
            "notes": self.notes,
            "last_synced": self.last_synced,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CharacterSheet":
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "Unnamed Character")),
            class_name=str(payload.get("class_name", "Adventurer")),
            subclass=str(payload.get("subclass", "")),
            level=int(payload.get("level", 1)),
            race=str(payload.get("race", "Unknown")),
            background=str(payload.get("background", "")),
            alignment=str(payload.get("alignment", "")),
            armor_class=int(payload.get("armor_class", 10)),
            hit_points=int(payload.get("hit_points", 0)),
            hit_points_max=int(payload.get("hit_points_max", 0)),
            speed=int(payload.get("speed", 30)),
            proficiency_bonus=int(payload.get("proficiency_bonus", 2)),
            abilities={str(key): int(value) for key, value in dict(payload.get("abilities", {})).items()},
            skills={str(key): str(value) for key, value in dict(payload.get("skills", {})).items()},
            attacks=[str(item) for item in payload.get("attacks", [])],
            spell_slots={str(key): int(value) for key, value in dict(payload.get("spell_slots", {})).items()},
            actions=[str(item) for item in payload.get("actions", [])],
            reactions=[str(item) for item in payload.get("reactions", [])],
            spells=[str(item) for item in payload.get("spells", [])],
            resources=[ResourceItem.from_dict(item) for item in payload.get("resources", [])],
            notes=str(payload.get("notes", "")),
            last_synced=payload.get("last_synced"),
            source=str(payload.get("source", "cached")),
        )

    def touch_sync(self) -> None:
        self.last_synced = datetime.now(tz=timezone.utc).isoformat()
        self.source = "synced"


@dataclass(slots=True)
class AppSettings:
    refresh_on_launch: bool = True
    preserve_browser_session: bool = True
    selected_character_id: str | None = None
    layout_mode: str = "dashboard"

    def to_dict(self) -> dict[str, Any]:
        return {
            "refresh_on_launch": self.refresh_on_launch,
            "preserve_browser_session": self.preserve_browser_session,
            "selected_character_id": self.selected_character_id,
            "layout_mode": self.layout_mode,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AppSettings":
        return cls(
            refresh_on_launch=bool(payload.get("refresh_on_launch", True)),
            preserve_browser_session=bool(payload.get("preserve_browser_session", True)),
            selected_character_id=payload.get("selected_character_id"),
            layout_mode=str(payload.get("layout_mode", "dashboard")),
        )
