# engine/decision.py
from typing import Dict, Any, List
import re

# Tunables
PERFECT_MATCH_THRESHOLD = 0.50  # 50% keyword overlap to count as "perfect action"
LOWER_VARIANCE = 0.10  # ±10%  variance when applying perfect outcome


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def jaccard_overlap(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    return (len(sa & sb) / len(sa | sb)) if (sa and sb) else 0.0


def classify_category(order_text: str) -> str:
    t = order_text.lower()
    if any(w in t for w in ["fortify", "attack", "march", "train", "garrison", "raid", "war"]):
        return "military"
    if any(w in t for w in ["trade", "tax", "market", "mint", "harvest", "tribute", "merchant"]):
        return "economy"
    if any(w in t for w in ["ally", "treaty", "envoy", "negotiate", "sanction", "peace"]):
        return "diplomacy"
    if any(
        w in t
        for w in ["temple", "priest", "festival", "edict", "faith", "religion", "church", "God"]
    ):
        return "religion"
    return "generic"


def match_perfect_action(order: str, perfect_block: dict):
    """
    Determines whether the player's order matches a perfect-run action.
    Requires at least two keyword hits OR >0.7 phrase similarity.
    """
    from difflib import SequenceMatcher

    order_lower = order.lower().strip()
    ideal_actions = perfect_block.get("ideal_actions", {})
    if not ideal_actions:
        return None

    best_match = None
    best_score = 0.0

    for action_name, data in ideal_actions.items():
        keywords = [kw.lower() for kw in data.get("keywords", [])]
        matches = sum(1 for kw in keywords if kw in order_lower)
        ratio = SequenceMatcher(None, order_lower, " ".join(keywords)).ratio()

        # now require stronger overlap
        if matches >= 2 or ratio > 0.7:
            if ratio > best_score:
                best_score = ratio
                best_match = data

    if best_match:
        print(f"[Perfect Run Detected] ({best_score:.2f}) {best_match.get('summary', '')[:60]}...")
        return best_match

    return None


def apply_small_variance(
    effect: Dict[str, Any], variance: float = LOWER_VARIANCE
) -> Dict[str, Any]:
    # Deterministic (no RNG) —  keep outcomes stable for good ideas

    return effect
