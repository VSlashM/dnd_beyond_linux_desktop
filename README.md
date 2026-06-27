# D&D Beyond Desktop Companion

A lightweight Python desktop application for viewing and interacting with D&D Beyond character data and owned resources.

## Current scope

- Native desktop UI
- One account, multiple characters
- Local cache for offline use
- Manual refresh and refresh-on-launch support
- Read-only character and resource viewing
- Search/filter across characters
- Dashboard and focused layout modes
- Extended notes section

## Project status

The first scaffold focuses on the local app shell, data model, and storage layer. Browser automation for D&D Beyond is intentionally isolated behind a sync adapter so it can be wired in without rewriting the UI.

## Run locally

Run the app with one command from the repository root:

```bash
bash run.sh
```

The script creates a local `.venv` if needed, installs the package in editable mode, and starts the desktop app.

It always tears down and recreates `.venv` first so stale packages or interpreter state cannot leak into the run.

If your Linux install does not include `tkinter`, install it once first:

```bash
sudo apt install python3-tk
```

## Scraping support

Browser automation is planned as a best-effort adapter. Once the login/session flow and page selectors are wired in, install the scraping extra:

```bash
pip install -e ".[scraping]"
playwright install
```

## UI stack

The current scaffold uses Python's standard library `tkinter` module so it can run without third-party desktop UI dependencies on a fresh Python installation.

## Next steps

- Wire the browser automation adapter to real D&D Beyond pages.
- Add a settings screen for refresh behavior and session persistence.
- Improve resource browsing and character detail rendering.
