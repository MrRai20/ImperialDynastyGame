# engine/loader.py
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import json
from pathlib import Path
import json

def load_save_state(scenario: dict, save_path: str):
    """
    Load previous game log and resume from last saved state.
    """
    try:
        with open(save_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        if not entries:
            print("No previous save found — starting fresh.")
            return scenario

        last_entry = entries[-1]
        last_turn = last_entry.get("turn", 1)
        last_resources = last_entry.get("resources_after", {})

        # update scenario save_state
        scenario["save_state"]["current_turn"] = last_turn + 1
        scenario["factions"]["Sparta"]["resources"].update(last_resources)
        print(f"\n[Loaded Save] Resuming from turn {last_turn + 1}")
        return scenario

    except FileNotFoundError:
        print("No save file found — starting new game.")
        return scenario


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_engine(core_path: Path) -> Dict[str, Any]:
    return load_json(core_path)

def load_scenario(scenario_path: Path) -> Dict[str, Any]:
    scenario = load_json(scenario_path)
    # Ensure a stable campaign id exists for perfect_run lookup
    meta = scenario.get("campaign_meta", {})
    if "id" not in meta:
        # Fallback: derive from filename (e.g., Sparta_380BC)
        scenario_id = scenario_path.stem.split("_", 2)[:2]
        meta["id"] = "_".join(scenario_id) if scenario_id else scenario_path.stem
        scenario["campaign_meta"] = meta
    return scenario

def load_perfect_run(perfect_run_path: Path) -> Dict[str, Any]:
    return load_json(perfect_run_path)

def select_perfect_block(scenario: Dict[str, Any], perfect_run: Dict[str, Any]) -> Dict[str, Any]:
    scenario_id = scenario.get("campaign_meta", {}).get("id")
    block = perfect_run.get(scenario_id, {})
    # Support nested faction blocks if present
    pf = scenario.get("player_faction") or first_faction_name(scenario)
    if "factions" in block:
        return block["factions"].get(pf, {})
    return block

def first_faction_name(scenario: Dict[str, Any]) -> str:
    factions = scenario.get("factions", {})
    return next(iter(factions.keys())) if factions else "Unknown"

def get_player_handles(scenario: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Return (player_faction_name, faction_data)."""
    pf = scenario.get("player_faction") or first_faction_name(scenario)
    fdata = scenario.get("factions", {}).get(pf, {})
    return pf, fdata

def save_game_state(log: list, path: Path):
    """
    Writes the current turn log to a save file.
    """
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)
        print(f"\n💾 Game saved successfully to {path.name}")
    except Exception as e:
        print(f"❌ Error saving game: {e}")


def load_game_state(scenario: dict, path: Path):
    """
    Loads game progress from an existing turn log.
    Returns updated scenario with new turn/resource state.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            entries = json.load(f)
        if not entries:
            print("⚠️ Save file is empty.")
            return scenario, []

        last_entry = entries[-1]
        last_turn = last_entry.get("turn", 1)
        last_resources = last_entry.get("resources_after", {})

        scenario["save_state"]["current_turn"] = last_turn + 1
        # find active faction dynamically if available
        for faction_name, data in scenario.get("factions", {}).items():
            if "resources" in data:
                data["resources"].update(last_resources)
                break

        print(f"\n📂 Loaded save: Turn {last_turn + 1}, resources restored.")
        return scenario, entries

    except FileNotFoundError:
        print("❌ No save file found.")
        return scenario, []
    except json.JSONDecodeError:
        print("❌ Corrupted save file.")
        return scenario, []
