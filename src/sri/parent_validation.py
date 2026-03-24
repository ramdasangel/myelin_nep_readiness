"""
Instrument 2: Parent Validation Signal
  - 5 Likert questions (Strongly Disagree → Strongly Agree)
  - Respondents: Parents (anonymous, 1 per student)
  - Score: 0-7 (ParentReadiness = 7 × ParentIndex)
  - NOT YET collected — this module is ready for when data arrives

Scoring:
  Strongly Disagree = 0, Disagree = 0.25, Neutral = 0.5,
  Agree = 0.75, Strongly Agree = 1.0
"""

from .constants import (
    PARENT_LIKERT_MAP,
    PARENT_INTERPRETATION_BANDS,
    PARENT_MIN_RESPONSE_RATE,
    PARENT_QUESTION_CODES,
)


def likert_to_score(selected_option):
    """Convert Likert selectedOption index to 0-1 score."""
    return PARENT_LIKERT_MAP.get(selected_option, 0.5)


def score_single_response(responses):
    """
    Score a single parent's response.

    Args:
        responses: list of dicts with 'questionCode' (P1-P5) and 'selectedOption'

    Returns:
        dict with:
            items: dict P1-P5 → score (0-1)
            parent_index: float 0-1
            parent_readiness: float 0-7
    """
    items = {}
    for code in PARENT_QUESTION_CODES:
        items[code] = 0.5  # default neutral

    for r in responses:
        code = r.get("questionCode", "")
        if code in items:
            items[code] = likert_to_score(r.get("selectedOption", 2))

    parent_index = sum(items.values()) / len(items)
    parent_readiness = 7 * parent_index

    return {
        "items": items,
        "parent_index": parent_index,
        "parent_readiness": parent_readiness,
    }


def score_branch(parent_responses, total_students):
    """
    Aggregate parent validation scores for a branch.

    Args:
        parent_responses: list of individual parent response sets
        total_students: total students in branch (for response rate)

    Returns:
        dict with:
            parent_index: float 0-1
            parent_readiness: float 0-7
            band: str
            response_rate: float
            meets_threshold: bool
            respondent_count: int
    """
    if not parent_responses:
        return {
            "parent_index": 0.0,
            "parent_readiness": 0.0,
            "band": "no_data",
            "response_rate": 0.0,
            "meets_threshold": False,
            "respondent_count": 0,
        }

    scored = [score_single_response(pr) for pr in parent_responses]

    # Aggregate: mean of all parent indices
    mean_index = sum(s["parent_index"] for s in scored) / len(scored)
    parent_readiness = 7 * mean_index

    # Response rate
    response_rate = len(scored) / total_students if total_students > 0 else 0.0
    meets_threshold = response_rate >= PARENT_MIN_RESPONSE_RATE

    # Band
    band = "no_data"
    for band_name, (lo, hi) in PARENT_INTERPRETATION_BANDS.items():
        if lo <= parent_readiness <= hi:
            band = band_name
            break

    # Per-question aggregation
    item_means = {}
    for code in PARENT_QUESTION_CODES:
        item_means[code] = sum(s["items"][code] for s in scored) / len(scored)

    return {
        "parent_index": mean_index,
        "parent_readiness": parent_readiness,
        "band": band,
        "response_rate": response_rate,
        "meets_threshold": meets_threshold,
        "respondent_count": len(scored),
        "item_means": item_means,
    }
