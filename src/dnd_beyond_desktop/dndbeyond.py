from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from .models import CharacterSheet


class SyncAdapter(Protocol):
    def refresh_characters(self, current_characters: list[CharacterSheet]) -> tuple[list[CharacterSheet], str]:
        ...


@dataclass(slots=True)
class BestEffortBrowserAdapter:
    session_dir: Path

    def refresh_characters(self, current_characters: list[CharacterSheet]) -> tuple[list[CharacterSheet], str]:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError:
            return current_characters, "Playwright is not installed yet; using the local cache."

        # Best-effort placeholder: keep the current cache intact until real selectors are wired in.
        # The persistent session directory is already in place for future login reuse.
        _ = sync_playwright
        for character in current_characters:
            character.last_synced = datetime.now(tz=timezone.utc).isoformat()
            character.source = "cached"
        return current_characters, f"Browser automation is wired for later use. Session dir: {self.session_dir}"
