[![CI](https://github.com/MrRai20/ImperialDynastyGame/actions/workflows/ci.yml/badge.svg)](https://github.com/MrRai20/ImperialDynastyGame/actions/workflows/ci.yml)
[![Tests](https://github.com/MrRai20/ImperialDynastyGame/actions/workflows/test.yml/badge.svg)](https://github.com/MrRai20/ImperialDynastyGame/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/MrRai20/ImperialDynastyGame?display_name=tag&sort=semver)](https://github.com/MrRai20/ImperialDynastyGame/releases)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MrRai20/ImperialDynastyGame)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.10–3.11](https://img.shields.io/badge/python-3.10–3.11-blue.svg)



# Imperial Dynasties — Sparta 380 BC (CLI)

A small historical strategy simulation you can play in the terminal. Built with pure Python.


---

### Quick Run

```bash
# Regular play
python cli.py

# Choose another scenario
python cli.py --scenario scenarios/Jerusalem_1185_AU_BaldwinLives.json

# CI/demo mode (auto exits)
python cli.py --auto-end





When prompted, type actions (e.g., `reform council`, `mobilize`, `report`, `save`, `load`, `briefing`, or `end`).

## Play in 1 click (GitHub Codespaces)

1. Fork this repo.
2. Click **Code → Codespaces → Create codespace on main**.
3. In the Codespace terminal run:
   ```bash
   python cli.py                 # interactive
   # or:
   python cli.py --auto-end      # quick demo, auto-exits


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

## Security

**What we do**
- **Static analysis (Bandit):** runs in CI (`bandit -q -r .`) to flag common Python issues (e.g., unsafe eval, weak crypto).
- **Dependency audit (pip-audit):** checks for known CVEs in pip packages during CI.
- **No secrets in repo:** saves/logs are ignored via `.gitignore`; no API keys or tokens.
- **Graceful I/O:** the CLI accepts only plain-text commands; save/load use JSON with basic validation.
- **Non-interactive fail-safe:** CI smoke run uses `cli.py --auto-end`, preventing interactive hangs.

**How to run locally**
```bash
# Static analysis
python -m pip install bandit
bandit -q -r .

# Dependency vulnerabilities
python -m pip install pip-audit
pip-audit -q

## License

MIT — see `LICENSE`.

## Recruiter Notes (How to Play)

- Clone/fork and run `python3 main.py`.
- Try commands: `briefing`, then `mobilize`, then `report`, `end`.
- The year counter correctly advances across BC→AD with no year 0.

---
If you hit issues running, open an Issue with your OS, Python version, and the error message.
