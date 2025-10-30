# engine/outcome.py
from typing import Dict, Any
import math

# Tunables for fallback (non-perfect) path
QUALITY_THRESHOLDS = {
    "major_success": 85,
    "success": 70,
    "mixed": 55,
    "failure": 40,
    "disaster": 0
}
MAX_FLAVOUR_VARIANCE = 0.10  # ±10%, but we keep “good idea” bias

PHRASES = {
    "major_success": [
        "A decisive advance; the realm takes notice.",
        "Superb execution delivers strategic advantage."
    ],
    "success": [
        "The plan succeeds with manageable costs.",
        "Clear gains achieved; momentum improves."
    ],
    "mixed": [
        "Mixed results; progress tempered by setbacks.",
        "Limited gains before resistance stiffens."
    ],
    "failure": [
        "The operation falters; resources strained.",
        "Outcomes disappoint; opposition adapts."
    ],
    "disaster": [
        "Severe reversal; morale and coffers suffer.",
        "A compounding error leads to cascading setbacks."
    ],
}

def context_modifier(faction: Dict[str, Any], category: str) -> int:
    traits = faction.get("context", {}).get("traits", [])
    mod = 0
    if category == "military":
        if "land_power" in traits: mod += 8
        if "naval_power" in traits: mod -= 3
    if category == "economy":
        if "trade_empire" in traits: mod += 6
        if "warrior_culture" in traits: mod -= 2
    if category == "diplomacy":
        if "democracy" in traits: mod += 4
        if "oligarchy" in traits: mod -= 2
    if category == "religion":
        if "theocracy" in traits: mod += 5
    return mod

def compute_quality_score(base_stat: int, ctx_mod: int, idea_quality: int) -> int:
    """
    Deterministic “skill-first” scoring:
    - base_stat: faction stat for category (0..20 typical)
    - ctx_mod: derived from traits (+/-)
    - idea_quality: 0 poor, 1 decent, 2 good
    No raw RNG; we clamp then map to quality bands.
    """
    # Weight idea quality highest; small flavour comes from ctx/base
    score = (idea_quality * 35) + (base_stat * 2) + (ctx_mod * 2)
    return max(0, min(100, score))

def quality_band(score: int) -> str:
    for label, thr in QUALITY_THRESHOLDS.items():
        if score >= thr:
            return label
    return "disaster"

def fallback_effects(category: str, band: str) -> Dict[str, int]:
    table = {
        "military": {
            "major_success": {"gold": -80, "manpower": -40, "authority": +4, "stability": +1},
            "success":        {"gold": -60, "manpower": -80, "authority": +2, "stability":  0},
            "mixed":          {"gold": -40, "manpower":  -150, "authority":  0, "stability":  0},
            "failure":        {"gold": -30, "manpower":  -250, "authority": -2, "stability": -1},
            "disaster":       {"gold": -60, "manpower": -400, "authority": -4, "stability": -2},
        },
        "economy": {
            "major_success": {"gold": +200, "authority": +2, "stability": +1, "legitimacy": +1},
            "success":        {"gold": +120, "authority": +1, "stability":  0},
            "mixed":          {"gold":  +40},
            "failure":        {"gold":  -40, "authority": -1},
            "disaster":       {"gold": -120, "authority": -3, "stability": -1},
        },
        "diplomacy": {
            "major_success": {"authority": +4, "legitimacy": +2, "stability": +1},
            "success":        {"authority": +2, "legitimacy": +1},
            "mixed":          {},
            "failure":        {"authority": -2},
            "disaster":       {"authority": -4, "legitimacy": -2},
        },
        "religion": {
            "major_success": {"gold": -20, "authority": +4, "legitimacy": +2, "stability": +1},
            "success":        {"gold": -10, "authority": +2, "legitimacy": +1},
            "mixed":          {"gold": -10},
            "failure":        {"gold": -10, "authority": -1},
            "disaster":       {"gold": -20, "authority": -3, "stability": -1},
        },
        "generic": {
            "major_success": {"gold": +40, "manpower": +20, "authority": +1},
            "success":        {"gold": +20, "manpower": +10, "authority": +1},
            "mixed":          {},
            "failure":        {"gold": -10, "manpower": -10, "authority": -1},
            "disaster":       {"gold": -30, "manpower": -30, "authority": -2},
        }
    }
    return table.get(category, table["generic"])[band]



def compose_summary(category: str, band: str) -> str:
   
    return PHRASES[band][0]

def apply_effects(resources: Dict[str, int], delta: Dict[str, int]) -> Dict[str, int]:
    for k, v in delta.items():
        resources[k] = resources.get(k, 0) + v
    return resources
