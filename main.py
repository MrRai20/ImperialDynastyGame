# main.py
from pathlib import Path
import json
from datetime import datetime

from engine.loader import (
    load_engine, load_scenario, load_perfect_run,
    select_perfect_block, get_player_handles,
    save_game_state, load_game_state
)
from engine.decisions import classify_category, match_perfect_action
from engine.outcome import (
    context_modifier, compute_quality_score, quality_band,
    fallback_effects, compose_summary, apply_effects
)

# ─────────────────────────────────────────────────────────────
# Paths and constants
ROOT = Path(__file__).parent
CORE_PATH = ROOT / "core" / "ImperiumMundi_Engine_Core_v1.1.json"
PERFECT_RUN_PATH = ROOT / "core" / "perfect_run.json"
SCENARIO_PATH = ROOT / "scenarios" / "Sparta_380BC_LastKing.json"

# ─────────────────────────────────────────────────────────────

def check_end_conditions(resources: dict, turn: int) -> str | None:
    if turn >= 40:
        return "Forty years have passed. The age of reform draws to a close."
    if resources.get("stability", 0) <= -5:
        return "Civil unrest erupts. The Spartan state collapses into chaos."
    if resources.get("authority", 0) <= -10:
        return "Your rule crumbles. Power shifts to rival factions."
    if resources.get("manpower", 0) <= 0:
        return "Your rule crumbles. Power shifts to rival factions."
    if resources.get("gold", 0) <= 0:
        return "Your rule crumbles. Power shifts to rival factions."
    if resources.get("stability", 0) >= 100:
        return "Your reforms succeed beyond expectation — a new golden age dawns."
    if resources.get("authority", 0) >= 100:
        return "Your reforms succeed beyond expectation — a new golden age dawns."
    return None

def save_log(entries, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)

def print_resources(resources: dict, header: str = None):
    if header:
        print(header)
    for k, v in resources.items():
        print(f" - {k.capitalize()}: {v}")

def parse_year(value) -> int:
    """
    Normalize scenario years to signed int:
    - '380 BC'/'380BC' -> -380
    - '379 AD'/'379AD' -> 379
    - integers pass through
    """
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return -380
    s = value.strip().upper().replace(" ", "")
    if s.endswith("BC"):
        num = s[:-2]
        return -int(num) if num.isdigit() else -380
    if s.endswith("AD"):
        num = s[:-2]
        return int(num) if num.isdigit() else 1
    # Bare number string: assume BC if scenario title contains BC elsewhere; default to negative.
    try:
        n = int(s)
        return n
    except ValueError:
        return -380  # defensible default for this scenario

def display_year(year: int) -> str:
    if year > 0:
        return f"{year} AD"
    else:
        return f"{abs(year)} BC"

def advance_year(year: int) -> int:
    """
    Move forward one historical year.
    Skips year 0 (there is none).
    """
    nxt = year + 1  # advancing time: -380 -> -379 (379 BC), -1 -> 0 (to be skipped), 1 -> 2 AD
    if nxt == 0:
        return 1
    return nxt

def calendar_distance(start: int, current: int) -> int:
    """
    Elapsed whole years from start to current going forward, with no year 0.
    Useful for decade indexing. Assumes current is >= start in chronology.
    """
    # If we cross from BC (<= -1) to AD (>= 1), subtract the missing year 0.
    crosses_zero = (start <= -1) and (current >= 1)
    raw = current - start
    return raw - (1 if crosses_zero else 0)

def main():
    used_perfect_actions = set()

    # ─── Load core data ───────────────────────────────────────
    _engine = load_engine(CORE_PATH)
    scenario = load_scenario(SCENARIO_PATH)
    perfect_run = load_perfect_run(PERFECT_RUN_PATH)
    perfect_block = select_perfect_block(scenario, perfect_run)
    pf_name, pf_data = get_player_handles(scenario)
    SAVE_PATH = ROOT / f"turn_log_{pf_name.lower()}.json"

    resources = {
        "gold": pf_data.get("resources", {}).get("gold", 1000),
        "manpower": pf_data.get("resources", {}).get("manpower", 1000),
        "authority": pf_data.get("resources", {}).get("authority", 0),
        "legitimacy": pf_data.get("resources", {}).get("legitimacy", 0),
        "stability": pf_data.get("resources", {}).get("stability", 0),
    }

    title = scenario.get("campaign_meta", {}).get("title", SCENARIO_PATH.stem)
    # Parse user-facing 'year' for briefing line only.
    year_str = scenario.get("save_state", {}).get("turn_year", "N/A")
    year_for_briefing = parse_year(year_str)
    # Use normalized signed int for the simulation counter.
    turn_year = parse_year(scenario.get("save_state", {}).get("turn_year", -380))
    # Snapshot the chronological starting year for decade calculations.
    start_turn_year = turn_year
    turn = scenario.get("save_state", {}).get("current_turn", 1)

    # ─── UI header ─────────────────────────────────────────────
    print("\n=== Imperial Dynasties — Historical Simulation Demo ===")
    print(f"Scenario: {title}")
    print(f"Year: {display_year(turn_year)} | Faction: {pf_name}")
    print("----------------------------------------------")
    print_resources(resources, header="Initial Resources:")
    print("----------------------------------------------")

    # ─── Scenario Briefing ──────────────────────────────────────
    context = (
        scenario.get("context")
        or scenario.get("factions", {}).get(pf_name, {}).get("context", {}).get("notes", None)
        or "No contextual data available."
    )
    objectives = scenario.get("objectives", [])

    print("\n=== STRATEGIC BRIEFING ===")
    print(f"Year: {display_year(year_for_briefing)} — {pf_name}")
    print(f"Context: {context}")
    print("\nPrimary Objectives:")
    for i, goal in enumerate(objectives, start=1):
        print(f"  {i}. {goal}")
    print("===========================\n")

    log = []

    # ─── Main Game Loop ───────────────────────────────────────
    while True:
        print(f"\n==== Turn {turn} | Year: {display_year(turn_year)} ====")

        order = input(
            "\nEnter order ('report', 'briefing', 'save', 'load', or 'end' to finish):\n>>> "
        ).strip()

        if order.lower() in {"end", "quit", "exit"}:
            break

        if order.lower() == "save":
            save_game_state(log, SAVE_PATH)
            continue

        if order.lower() == "load":
            scenario, log = load_game_state(scenario, SAVE_PATH)
            pf_name, pf_data = get_player_handles(scenario)
            resources = pf_data.get("resources", resources)
            # Why: keep counters coherent after load.
            turn_year = parse_year(scenario.get("save_state", {}).get("turn_year", turn_year))
            start_turn_year = parse_year(scenario.get("save_state", {}).get("start_turn_year", start_turn_year))
            turn = scenario.get("save_state", {}).get("current_turn", turn)
            continue

        if order.lower() == "briefing":
            print("\n=== STRATEGIC BRIEFING ===")
            print(f"Year: {display_year(turn_year)} — {pf_name}")
            print(f"Context: {scenario.get('context', 'No contextual data.')}")
            print("\nPrimary Objectives:")
            for i, goal in enumerate(scenario.get('objectives', []), start=1):
                print(f"  {i}. {goal}")
            print("===========================\n")
            continue

        if order.lower() == "report":
            sblock = perfect_run.get("Sparta_380BC", {})
            outcome = sblock.get("simulation_outcome", {})

            current_year = turn_year
            elapsed = max(0, calendar_distance(start_turn_year, current_year))
            decade_index = (elapsed // 10) + 1  # 1..N

            if decade_index > 4:
                decade_key = "final_metrics"
            else:
                start_year_bc = 380 - ((decade_index - 1) * 10)
                end_year_bc = start_year_bc - 10
                decade_key = f"decade_{decade_index}_{start_year_bc}_{end_year_bc}"

            print("\n========== REPORT ==========")
            d = outcome.get(decade_key)
            if d:
                if decade_key == "final_metrics":
                    print(f"[FINAL REPORT] {d.get('overall_outcome', 'No summary available.')}")
                else:
                    print(f"[{decade_key}] {d.get('summary', 'No summary available.')}")
            else:
                final = outcome.get("final_metrics", {})
                if final:
                    print(f"[FINAL REPORT] {final.get('overall_outcome', 'No summary available.')}")
                else:
                    print("[REPORT] No data for this period.")

            print_resources(resources, header="\nCurrent Resources:")
            print("============================\n")
            continue

        # ── Action handling ────────────────────────────────────
        delta = {}
        summary = ""
        band = ""

        best = match_perfect_action(order, perfect_block)

        if best:
            action_key = best.get("summary", "")[:30]
            if action_key in used_perfect_actions:
                print("[⚠️ Perfect Run Denied] That strategy has already been executed.")
                delta = {"authority": -1}
                summary = "Repetition breeds stagnation — the same policy yields diminishing returns."
                band = "failure"
            else:
                used_perfect_actions.add(action_key)
                delta = best["effect"]
                summary = best["summary"]
                band = "major_success"
        else:
            category = classify_category(order)
            faction = scenario.get("factions", {}).get(pf_name, {})
            stats = faction.get("stats", {})
            base_stat = stats.get(category, 5)
            ctx_mod = context_modifier(faction, category)
            idea_quality = 1
            score = compute_quality_score(base_stat, ctx_mod, idea_quality)
            band = quality_band(score)
            delta = fallback_effects(category, band)
            summary = compose_summary(category, band)

        resources = apply_effects(resources, delta)
        entry = {
            "turn": turn,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "order": order,
            "band": band,
            "summary": summary,
            "delta": delta,
            "resources_after": resources.copy(),
            "year_after": turn_year,
        }
        log.append(entry)

        delta_str = " | ".join([f"{k}: {('+' if v >= 0 else '')}{v}" for k, v in delta.items()])
        print(f"\nOutcome: {summary}")
        print(f"Δ {delta_str if delta_str else 'no change'}")

        totals_str = " | ".join([f"{k}: {v}" for k, v in resources.items()])
        print(f"Current Totals → {totals_str}")

        # Advance time (forward chronology)
        turn += 1
        turn_year = advance_year(turn_year)
        scenario.setdefault("save_state", {})["turn_year"] = turn_year
        scenario["save_state"]["current_turn"] = turn
        scenario["save_state"]["start_turn_year"] = start_turn_year  # Why: keep for accurate reports.

        end_msg = check_end_conditions(resources, turn)
        if end_msg:
            print(f"\n=== CAMPAIGN CONCLUDED ===\n{end_msg}\n")
            save_log(log, ROOT / "final_save.json")
            print("Final save written as 'final_save.json'")
            break

    save_log(log, SAVE_PATH)
    print("\nSession saved to turn_log.json")
    print("Thank you for playing Imperial Dynasties.")

if __name__ == "__main__":
    main()
