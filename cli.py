"""
Wrapper for ImperialDynastyGame.

Adds:
- --scenario <file>: temporarily swap any scenario JSON into the slot main.py expects.
- --auto-end: start the game and automatically exit (sends 'end' to stdin).

Keeps main.py unchanged.
"""

from __future__ import annotations
import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager

REPO_ROOT = pathlib.Path(__file__).resolve().parent
HARDCODED_SCENARIO = REPO_ROOT / "scenarios" / "Sparta_380BC_LastKing.json"


@contextmanager
def temporary_swap(target: pathlib.Path, source: pathlib.Path | None):
    backup = None
    try:
        if source:
            src = pathlib.Path(source).resolve()
            tgt = target.resolve()
            if src != tgt:
                if not src.exists():
                    raise FileNotFoundError(f"Scenario not found: {src}")
                if tgt.exists():
                    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="scenario_bak_"))
                    backup = tmpdir / tgt.name
                    shutil.copy2(tgt, backup)
                shutil.copy2(src, tgt)
        yield
    finally:
        if backup and backup.exists():
            try:
                shutil.copy2(backup, target)
            except Exception:
                pass


def run_game(auto_end: bool) -> int:
    cmd = [sys.executable, "main.py"]
    if not auto_end:
        return subprocess.call(cmd)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
    try:
        p.communicate("end\n", timeout=15)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass
    return 0


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="ImperialDynastyGame launcher")
    ap.add_argument("--scenario", help="Path to scenario JSON to run.")
    ap.add_argument("--auto-end", action="store_true", help="Auto-exit (sends 'end').")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    scenario_path = pathlib.Path(args.scenario).resolve() if args.scenario else None
    with temporary_swap(HARDCODED_SCENARIO, scenario_path):
        return run_game(args.auto_end)


if __name__ == "__main__":
    raise SystemExit(main())
