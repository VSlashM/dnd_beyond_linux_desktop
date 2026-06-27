from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .demo_data import load_demo_characters
from .models import AppSettings, CharacterSheet


class AppStorage:
    def __init__(self, app_name: str = "dnd_beyond_desktop") -> None:
        self.root = self._resolve_data_dir(app_name)
        self.root.mkdir(parents=True, exist_ok=True)
        self.characters_path = self.root / "characters.json"
        self.settings_path = self.root / "settings.json"
        self.session_dir = self.root / "browser-session"
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_data_dir(self, app_name: str) -> Path:
        base_dir = os.environ.get("XDG_DATA_HOME")
        if base_dir:
            return Path(base_dir) / app_name
        return Path.home() / ".local" / "share" / app_name

    def load_settings(self) -> AppSettings:
        if not self.settings_path.exists():
            return AppSettings()
        payload = self._read_json(self.settings_path)
        return AppSettings.from_dict(payload)

    def save_settings(self, settings: AppSettings) -> None:
        self._write_json(self.settings_path, settings.to_dict())

    def load_characters(self) -> list[CharacterSheet]:
        if not self.characters_path.exists():
            return load_demo_characters()
        payload = self._read_json(self.characters_path)
        return [CharacterSheet.from_dict(item) for item in payload]

    def save_characters(self, characters: list[CharacterSheet]) -> None:
        self._write_json(self.characters_path, [character.to_dict() for character in characters])

    def save_character_notes(self, character_id: str, notes: str) -> None:
        characters = self.load_characters()
        changed = False
        for character in characters:
            if character.id == character_id:
                character.notes = notes
                changed = True
                break
        if changed:
            self.save_characters(characters)

    def _read_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_json(self, path: Path, payload: Any) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
