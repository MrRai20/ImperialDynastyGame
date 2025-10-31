import subprocess
import sys
import pathlib


def test_full_run():
    """Run Imperial Dynasty Game via cli in auto end mode"""
    root = pathlib.Path(__file__).resolve().parent.parent
    cli = root / "cli.py"

    results = subprocess.run(
        [sys.executable, str(cli), "--auto-end"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # basic expectations

    assert results.returncode == 0
    assert "Thank you for playing" in results.stdout
