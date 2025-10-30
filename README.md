[![CI](https://github.com/MrRai20/ImperialDynastyGame/actions/workflows/ci.yml/badge.svg)](https://github.com/MrRai20/ImperialDynastyGame/actions/workflows/ci.yml)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MrRai20/ImperialDynastyGame)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)


# Imperial Dynasties — Sparta 380 BC (CLI)

A small historical strategy simulation you can play in the terminal. Built with pure Python.

## Quick Start

```bash
git clone https://github.com/MrRai20/ImperialDynastyGame.git
cd imperial-dynasties
python3 -m pip install -r requirements.txt  # (none required right now)
python3 main.py
```

When prompted, type actions (e.g., `reform council`, `mobilize`, `report`, `save`, `load`, `briefing`, or `end`).

## Play in 1 click (GitHub Codespaces)

1. Fork this repo.
2. Click **Code → Codespaces → Create codespace on main**.
3. In the Codespace terminal run: `python3 main.py`.

> Codespaces uses `.devcontainer/devcontainer.json` so everything just works in-browser.

## Repository Layout

- `main.py` — game loop & CLI.
- `core/` — engine JSON data.
- `engine/` — engine modules.
- `scenarios/` — scenario JSON files.
- `turn_log_*.json` — created when you play.
- `final_save.json` — exported when a campaign ends.

## Save/Load

- `save` writes a log to `turn_log_<faction>.json`.
- `load` restores from that file if present.

## CI

- GitHub Actions (`.github/workflows/ci.yml`) lints with Ruff and does a non-interactive smoke run.
- Add tests under `tests/` and they'll run automatically.

## License

MIT — see `LICENSE`.

## Recruiter Notes (How to Play)

- Clone/fork and run `python3 main.py`.
- Try commands: `briefing`, then `mobilize`, then `report`, `end`.
- The year counter correctly advances across BC→AD with no year 0.

---
If you hit issues running, open an Issue with your OS, Python version, and the error message.
