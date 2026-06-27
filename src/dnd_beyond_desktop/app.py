from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .dndbeyond import BestEffortBrowserAdapter
from .models import AppSettings, CharacterSheet
from .storage import AppStorage


class MainWindow:
    SKILL_MAP: dict[str, str] = {
        "Acrobatics": "DEX",
        "Animal Handling": "WIS",
        "Arcana": "INT",
        "Athletics": "STR",
        "Deception": "CHA",
        "History": "INT",
        "Insight": "WIS",
        "Intimidation": "CHA",
        "Investigation": "INT",
        "Medicine": "WIS",
        "Nature": "INT",
        "Perception": "WIS",
        "Performance": "CHA",
        "Persuasion": "CHA",
        "Religion": "INT",
        "Sleight of Hand": "DEX",
        "Stealth": "DEX",
        "Survival": "WIS",
    }

    def __init__(self, storage: AppStorage, settings: AppSettings, characters: list[CharacterSheet]) -> None:
        self.storage = storage
        self.settings = settings
        self.characters = characters
        self.filtered_characters = list(characters)
        self.current_character_id = settings.selected_character_id or (characters[0].id if characters else None)
        self.refresh_adapter = BestEffortBrowserAdapter(storage.session_dir)

        self.root = tk.Tk()
        self.root.title("D&D Beyond Desktop Companion")
        self.root.geometry("1400x920")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.note_save_after_id: str | None = None
        self.status_var = tk.StringVar(value="Ready")

        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        self.build_toolbar(outer)
        self.build_main_area(outer)

        ttk.Label(outer, textvariable=self.status_var, anchor="w").pack(fill="x", pady=(8, 0))

        if self.settings.refresh_on_launch:
            self.perform_refresh()
        else:
            self.refresh_character_views()

    def build_toolbar(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Label(toolbar, text="Search").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_search_filter())
        ttk.Entry(toolbar, textvariable=self.search_var).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        ttk.Label(toolbar, text="Character").grid(row=0, column=2, sticky="w")
        self.character_picker = ttk.Combobox(toolbar, state="readonly")
        self.character_picker.bind("<<ComboboxSelected>>", lambda *_: self.on_character_picker_changed())
        self.character_picker.grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(toolbar, text="Layout").grid(row=0, column=4, sticky="w")
        self.layout_var = tk.StringVar(value=self.settings.layout_mode)
        self.layout_picker = ttk.Combobox(toolbar, state="readonly", values=["dashboard", "focused"], textvariable=self.layout_var)
        self.layout_picker.bind("<<ComboboxSelected>>", lambda *_: self.on_layout_mode_changed())
        self.layout_picker.grid(row=0, column=5, sticky="ew", padx=(8, 12))

        ttk.Button(toolbar, text="Refresh", command=self.perform_refresh).grid(row=0, column=6, padx=(0, 8))
        ttk.Button(toolbar, text="Settings", command=self.open_settings_tab).grid(row=0, column=7)
        toolbar.columnconfigure(1, weight=2)
        toolbar.columnconfigure(3, weight=1)
        toolbar.columnconfigure(5, weight=1)

    def build_main_area(self, parent: ttk.Frame) -> None:
        self.main_pane = ttk.Panedwindow(parent, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True)

        self.left_panel = ttk.Frame(self.main_pane, padding=(0, 0, 8, 0))
        ttk.Label(self.left_panel, text="Characters").pack(anchor="w")
        list_frame = ttk.Frame(self.left_panel)
        list_frame.pack(fill="both", expand=True)
        self.character_list = tk.Listbox(list_frame, height=20)
        self.character_list.bind("<<ListboxSelect>>", lambda *_: self.on_character_list_selection_changed())
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.character_list.yview)
        self.character_list.configure(yscrollcommand=list_scrollbar.set)
        self.character_list.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")
        self.main_pane.add(self.left_panel, weight=1)

        self.detail_panel = ttk.Frame(self.main_pane)
        self.main_pane.add(self.detail_panel, weight=3)

        self.notebook = ttk.Notebook(self.detail_panel)
        self.notebook.pack(fill="both", expand=True)

        self.overview_tab = ttk.Frame(self.notebook, padding=12)
        self.resources_tab = ttk.Frame(self.notebook, padding=12)
        self.notes_tab = ttk.Frame(self.notebook, padding=12)
        self.settings_tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.resources_tab, text="Resources")
        self.notebook.add(self.notes_tab, text="Extended Notes")
        self.notebook.add(self.settings_tab, text="Settings")

        self.build_overview_tab()
        self.build_resources_tab()
        self.build_notes_tab()
        self.build_settings_tab()

        self.apply_layout_mode(self.settings.layout_mode)
        self.refresh_character_views()

    def build_overview_tab(self) -> None:
        self.overview_title = ttk.Label(self.overview_tab, text="Select a character to view details.", font=("TkDefaultFont", 16, "bold"))
        self.overview_title.pack(anchor="w")

        self.summary_label = ttk.Label(self.overview_tab, text="", wraplength=760, justify="left")
        self.summary_label.pack(anchor="w", pady=(8, 12))

        stats_box = ttk.LabelFrame(self.overview_tab, text="Core Stats")
        stats_box.pack(fill="x", pady=(0, 12))
        self.stats_labels: dict[str, ttk.Label] = {}
        for row, field in enumerate(["Armor Class", "Hit Points", "Speed", "Proficiency Bonus", "Race", "Background", "Alignment"]):
            ttk.Label(stats_box, text=field).grid(row=row, column=0, sticky="w", padx=8, pady=4)
            label = ttk.Label(stats_box, text="-")
            label.grid(row=row, column=1, sticky="w", padx=8, pady=4)
            self.stats_labels[field] = label

        abilities_box = ttk.LabelFrame(self.overview_tab, text="Ability Scores")
        abilities_box.pack(fill="x", pady=(0, 12))
        self.ability_labels: dict[str, ttk.Label] = {}
        for column, name in enumerate(["STR", "DEX", "CON", "INT", "WIS", "CHA"]):
            ttk.Label(abilities_box, text=name).grid(row=0, column=column, padx=8, pady=(8, 2))
            value_label = ttk.Label(abilities_box, text="-", font=("TkDefaultFont", 14, "bold"))
            value_label.grid(row=1, column=column, padx=8, pady=(0, 8))
            self.ability_labels[name] = value_label

        checks_box = ttk.LabelFrame(self.overview_tab, text="Ability Check Bonuses")
        checks_box.pack(fill="x", pady=(0, 12))
        check_style = ttk.Style()
        check_style.configure("Overview.Treeview", rowheight=28)
        self.ability_checks_tree = ttk.Treeview(checks_box, columns=("Ability", "Check Bonus"), show="headings", height=6, style="Overview.Treeview")
        self.ability_checks_tree.heading("Ability", text="Ability")
        self.ability_checks_tree.heading("Check Bonus", text="Check Bonus")
        self.ability_checks_tree.column("Ability", width=120, anchor="w")
        self.ability_checks_tree.column("Check Bonus", width=120, anchor="w")
        checks_scrollbar = ttk.Scrollbar(checks_box, orient="vertical", command=self.ability_checks_tree.yview)
        self.ability_checks_tree.configure(yscrollcommand=checks_scrollbar.set)
        self.ability_checks_tree.pack(side="left", fill="both", expand=True)
        checks_scrollbar.pack(side="right", fill="y")

        skills_box = ttk.LabelFrame(self.overview_tab, text="Skill Bonuses")
        skills_box.pack(fill="both", expand=True, pady=(0, 12))
        self.skills_tree = ttk.Treeview(skills_box, columns=("Skill", "Bonus"), show="headings", height=10, style="Overview.Treeview")
        self.skills_tree.heading("Skill", text="Skill")
        self.skills_tree.heading("Bonus", text="Bonus")
        self.skills_tree.column("Skill", width=220, anchor="w")
        self.skills_tree.column("Bonus", width=120, anchor="w")
        skills_scrollbar = ttk.Scrollbar(skills_box, orient="vertical", command=self.skills_tree.yview)
        self.skills_tree.configure(yscrollcommand=skills_scrollbar.set)
        self.skills_tree.pack(side="left", fill="both", expand=True)
        skills_scrollbar.pack(side="right", fill="y")

        saves_box = ttk.LabelFrame(self.overview_tab, text="Saving Throw Bonuses")
        saves_box.pack(fill="x", pady=(0, 12))
        self.saves_tree = ttk.Treeview(saves_box, columns=("Ability", "Bonus"), show="headings", height=6, style="Overview.Treeview")
        self.saves_tree.heading("Ability", text="Ability")
        self.saves_tree.heading("Bonus", text="Bonus")
        self.saves_tree.column("Ability", width=120, anchor="w")
        self.saves_tree.column("Bonus", width=120, anchor="w")
        saves_scrollbar = ttk.Scrollbar(saves_box, orient="vertical", command=self.saves_tree.yview)
        self.saves_tree.configure(yscrollcommand=saves_scrollbar.set)
        self.saves_tree.pack(side="left", fill="both", expand=True)
        saves_scrollbar.pack(side="right", fill="y")

        attacks_box = ttk.LabelFrame(self.overview_tab, text="Attacks and Actions")
        attacks_box.pack(fill="x")
        self.attacks_label = ttk.Label(attacks_box, text="", wraplength=760, justify="left")
        self.attacks_label.pack(anchor="w", padx=8, pady=8)

    def build_resources_tab(self) -> None:
        columns = ("Category", "Title", "Description", "Source")
        style = ttk.Style()
        style.configure("Resources.Treeview", rowheight=34)
        self.resources_tree = ttk.Treeview(self.resources_tab, columns=columns, show="headings", height=18, style="Resources.Treeview")
        for column in columns:
            self.resources_tree.heading(column, text=column)
            self.resources_tree.column(column, width=180 if column != "Description" else 420, anchor="w")
        y_scroll = ttk.Scrollbar(self.resources_tab, orient="vertical", command=self.resources_tree.yview)
        self.resources_tree.configure(yscrollcommand=y_scroll.set)
        self.resources_tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

    def build_notes_tab(self) -> None:
        ttk.Label(self.notes_tab, text="Extended Notes", font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        ttk.Label(
            self.notes_tab,
            text="Use this area for encounter reminders, tactics, shopping lists, campaign notes, or anything you want during play.",
            wraplength=780,
            justify="left",
        ).pack(anchor="w", pady=(4, 8))
        self.notes_editor = tk.Text(self.notes_tab, height=18, wrap="word")
        self.notes_editor.pack(fill="both", expand=True)
        self.notes_editor.bind("<<Modified>>", self.on_notes_modified)

    def build_settings_tab(self) -> None:
        ttk.Label(self.settings_tab, text="Settings", font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        ttk.Label(
            self.settings_tab,
            text="Tuning options for refresh behavior, session persistence, and layout preferences.",
            wraplength=780,
            justify="left",
        ).pack(anchor="w", pady=(4, 12))

        panel = ttk.Frame(self.settings_tab)
        panel.pack(fill="x")

        self.refresh_on_launch_var = tk.BooleanVar(value=self.settings.refresh_on_launch)
        self.refresh_session_var = tk.BooleanVar(value=self.settings.preserve_browser_session)

        prefs_box = ttk.LabelFrame(panel, text="Behavior")
        prefs_box.pack(fill="x", pady=(0, 12))

        ttk.Checkbutton(prefs_box, text="Refresh on launch", variable=self.refresh_on_launch_var, command=self.on_refresh_on_launch_toggled).pack(anchor="w", padx=10, pady=(10, 4))
        ttk.Checkbutton(prefs_box, text="Preserve browser session", variable=self.refresh_session_var, command=self.on_session_toggle).pack(anchor="w", padx=10, pady=(0, 10))

        layout_box = ttk.LabelFrame(panel, text="Layout")
        layout_box.pack(fill="x", pady=(0, 12))
        ttk.Label(layout_box, text="Default layout").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.settings_layout_var = tk.StringVar(value=self.settings.layout_mode)
        settings_layout_picker = ttk.Combobox(layout_box, state="readonly", values=["dashboard", "focused"], textvariable=self.settings_layout_var)
        settings_layout_picker.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)
        settings_layout_picker.bind("<<ComboboxSelected>>", lambda *_: self.on_layout_mode_changed())

        storage_box = ttk.LabelFrame(panel, text="Storage")
        storage_box.pack(fill="x")
        ttk.Label(storage_box, text="Local cache location").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))
        ttk.Label(storage_box, text=str(self.storage.root), wraplength=760, justify="left").grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))
        ttk.Label(storage_box, text="Browser session folder").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 4))
        ttk.Label(storage_box, text=str(self.storage.session_dir), wraplength=760, justify="left").grid(row=3, column=0, sticky="w", padx=10, pady=(0, 10))

        ttk.Button(self.settings_tab, text="Open focused view", command=self.open_focused_view).pack(anchor="w", pady=(12, 0))

    def refresh_character_views(self) -> None:
        search_text = self.search_var.get().strip().lower()
        self.filtered_characters = [character for character in self.characters if not search_text or search_text in character.search_blob()]

        self.character_list.delete(0, tk.END)
        picker_values: list[str] = []
        for character in self.filtered_characters:
            display = f"{character.name} — {character.headline()}"
            self.character_list.insert(tk.END, display)
            picker_values.append(display)

        self.character_picker["values"] = picker_values

        if not self.filtered_characters:
            self.clear_details("No characters matched the current search.")
            self.status_var.set("No matching characters")
            return

        selected_id = self.current_character_id or self.filtered_characters[0].id
        self.select_character(selected_id)

    def clear_details(self, message: str) -> None:
        self.overview_title.config(text=message)
        self.summary_label.config(text="")
        for label in self.stats_labels.values():
            label.config(text="-")
        for label in self.ability_labels.values():
            label.config(text="-")
        for row in self.ability_checks_tree.get_children():
            self.ability_checks_tree.delete(row)
        for row in self.skills_tree.get_children():
            self.skills_tree.delete(row)
        for row in self.saves_tree.get_children():
            self.saves_tree.delete(row)
        self.attacks_label.config(text="")
        for row in self.resources_tree.get_children():
            self.resources_tree.delete(row)
        self.notes_editor.delete("1.0", tk.END)

    def select_character(self, character_id: str | None) -> None:
        if not character_id:
            return

        matching = next((character for character in self.filtered_characters if character.id == character_id), None)
        if matching is None:
            matching = next((character for character in self.characters if character.id == character_id), None)
        if matching is None:
            return

        self.current_character_id = matching.id
        self.settings.selected_character_id = matching.id
        self.storage.save_settings(self.settings)

        display_value = f"{matching.name} — {matching.headline()}"
        if display_value in list(self.character_picker["values"]):
            self.character_picker.set(display_value)

        self.character_list.selection_clear(0, tk.END)
        for row in range(self.character_list.size()):
            if self.character_list.get(row) == display_value:
                self.character_list.selection_set(row)
                self.character_list.see(row)
                break

        self.populate_details(matching)

    def populate_details(self, character: CharacterSheet) -> None:
        self.overview_title.config(text=f"{character.name} — {character.headline()}")
        self.summary_label.config(
            text=f"{character.race} {character.class_name} | {character.background} | Last synced: {character.last_synced or 'never'}"
        )
        self.stats_labels["Armor Class"].config(text=str(character.armor_class))
        self.stats_labels["Hit Points"].config(text=f"{character.hit_points}/{character.hit_points_max}")
        self.stats_labels["Speed"].config(text=f"{character.speed} ft")
        self.stats_labels["Proficiency Bonus"].config(text=f"+{character.proficiency_bonus}")
        self.stats_labels["Race"].config(text=character.race)
        self.stats_labels["Background"].config(text=character.background)
        self.stats_labels["Alignment"].config(text=character.alignment)

        for ability, label in self.ability_labels.items():
            label.config(text=str(character.abilities.get(ability, "-")))

        for row in self.ability_checks_tree.get_children():
            self.ability_checks_tree.delete(row)
        for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            self.ability_checks_tree.insert("", tk.END, values=(ability, self.format_modifier(self.get_ability_modifier(character, ability))))

        for row in self.skills_tree.get_children():
            self.skills_tree.delete(row)
        for skill in self.SKILL_MAP:
            self.skills_tree.insert("", tk.END, values=(skill, self.get_skill_bonus(character, skill)))

        for row in self.saves_tree.get_children():
            self.saves_tree.delete(row)
        for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            self.saves_tree.insert("", tk.END, values=(ability, self.get_save_bonus(character, ability)))

        self.attacks_label.config(text="\n".join(f"• {attack}" for attack in character.attacks) or "No attacks loaded.")

        for row in self.resources_tree.get_children():
            self.resources_tree.delete(row)
        resource_rows = []
        for resource in character.resources:
            resource_rows.append((resource.category, resource.title, resource.description, resource.source))

        resource_rows.extend(("Action", action, "", "Character sheet") for action in character.actions)
        resource_rows.extend(("Reaction", reaction, "", "Character sheet") for reaction in character.reactions)
        resource_rows.extend(("Spell", spell, "", "Character sheet") for spell in character.spells)

        for row in resource_rows:
            self.resources_tree.insert("", tk.END, values=row)

        self.notes_editor.unbind("<<Modified>>")
        self.notes_editor.delete("1.0", tk.END)
        self.notes_editor.insert("1.0", character.notes)
        self.notes_editor.bind("<<Modified>>", self.on_notes_modified)
        self.notes_editor.edit_modified(False)
        self.status_var.set(f"Loaded {character.name}")

    def queue_note_save(self) -> None:
        if self.note_save_after_id is not None:
            self.root.after_cancel(self.note_save_after_id)
        self.note_save_after_id = self.root.after(500, self.save_current_notes)

    def save_current_notes(self) -> None:
        self.note_save_after_id = None
        if not self.current_character_id:
            return

        notes = self.notes_editor.get("1.0", tk.END).rstrip()
        self.storage.save_character_notes(self.current_character_id, notes)
        for character in self.characters:
            if character.id == self.current_character_id:
                character.notes = notes
                break
        self.status_var.set("Notes saved")

    def perform_refresh(self) -> None:
        refreshed, message = self.refresh_adapter.refresh_characters(self.characters)
        self.characters = refreshed
        self.storage.save_characters(self.characters)
        self.refresh_character_views()
        self.status_var.set(message)

    def apply_search_filter(self) -> None:
        self.refresh_character_views()

    def get_ability_modifier(self, character: CharacterSheet, ability: str) -> int:
        score = character.abilities.get(ability, 10)
        return (score - 10) // 2

    def format_modifier(self, modifier: int) -> str:
        return f"{modifier:+d}"

    def get_skill_bonus(self, character: CharacterSheet, skill: str) -> str:
        if skill in character.skills:
            return character.skills[skill]
        ability = self.SKILL_MAP[skill]
        return self.format_modifier(self.get_ability_modifier(character, ability))

    def get_save_bonus(self, character: CharacterSheet, ability: str) -> str:
        return self.format_modifier(self.get_ability_modifier(character, ability))

    def on_character_list_selection_changed(self) -> None:
        selection = self.character_list.curselection()
        if not selection:
            return
        index = selection[0]
        if 0 <= index < len(self.filtered_characters):
            self.select_character(self.filtered_characters[index].id)

    def on_character_picker_changed(self) -> None:
        selection = self.character_picker.current()
        if 0 <= selection < len(self.filtered_characters):
            self.select_character(self.filtered_characters[selection].id)

    def on_layout_mode_changed(self) -> None:
        layout_mode = self.layout_var.get()
        self.settings_layout_var.set(layout_mode)
        self.layout_var.set(layout_mode)
        self.apply_layout_mode(layout_mode)
        self.settings.layout_mode = layout_mode
        self.storage.save_settings(self.settings)

    def apply_layout_mode(self, layout_mode: str) -> None:
        dashboard_mode = layout_mode == "dashboard"
        panes = self.main_pane.panes()
        if dashboard_mode and str(self.left_panel) not in panes:
            self.main_pane.insert(0, self.left_panel, weight=1)
        elif not dashboard_mode and str(self.left_panel) in panes:
            self.main_pane.forget(self.left_panel)

    def on_refresh_on_launch_toggled(self) -> None:
        self.settings.refresh_on_launch = self.refresh_on_launch_var.get()
        self.storage.save_settings(self.settings)

    def on_session_toggle(self) -> None:
        self.settings.preserve_browser_session = self.refresh_session_var.get()
        self.storage.save_settings(self.settings)

    def open_settings_tab(self) -> None:
        self.notebook.select(self.settings_tab)

    def open_focused_view(self) -> None:
        self.layout_var.set("focused")
        self.settings_layout_var.set("focused")
        self.on_layout_mode_changed()
        self.notebook.select(self.overview_tab)

    def on_notes_modified(self, event: tk.Event) -> None:
        widget = event.widget
        if widget.edit_modified():
            widget.edit_modified(False)
            self.queue_note_save()

    def on_close(self) -> None:
        if self.note_save_after_id is not None:
            try:
                self.root.after_cancel(self.note_save_after_id)
            except tk.TclError:
                pass
            self.note_save_after_id = None

        self.save_current_notes()
        self.storage.save_settings(self.settings)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    storage = AppStorage()
    settings = storage.load_settings()
    characters = storage.load_characters()

    window = MainWindow(storage, settings, characters)
    window.run()