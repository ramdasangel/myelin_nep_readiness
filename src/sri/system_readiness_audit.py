"""
Instrument 1: SRI System Readiness Audit
  - 10 binary (Yes/No) questions
  - Respondents: Principal + VP + Academic Coordinator
  - Score: 0-20 (TeacherEnablement 0-10 + LeadershipRoutines 0-10)
  - setCode: SRI001

Data source: DiagnosticAttempt where setCode = "SRI001"
"""

from collections import defaultdict
from .constants import (
    SRI_BINARY_MAP,
    SRI_INTERPRETATION_BANDS,
    SRI_QUESTION_IDS,
    TEACHER_ENABLEMENT_CODES,
    LEADERSHIP_ROUTINE_CODES,
)


def _binary_value(selected_option):
    """Convert selectedOption index to binary 0/1."""
    return SRI_BINARY_MAP.get(selected_option, 0)


def score_single_attempt(responses, question_id_order=None):
    """
    Score a single SRI attempt from its responses array.

    Args:
        responses: list of dicts with 'questionId' and 'selectedOption'
        question_id_order: optional list of question IDs in canonical order
                          (defaults to SRI_QUESTION_IDS)

    Returns:
        dict with keys:
            enablement_items: dict E1-E5 → 0 or 1
            routine_items: dict R1-R5 → 0 or 1
            enablement_index: float 0-1
            routine_index: float 0-1
            teacher_enablement: float 0-10
            leadership_routines: float 0-10
            system_readiness: float 0-20
            band: str interpretation band
    """
    if question_id_order is None:
        question_id_order = SRI_QUESTION_IDS

    # Build response lookup: questionId → selectedOption
    resp_map = {}
    for r in responses:
        qid = str(r.get("questionId", r.get("_id", "")))
        resp_map[qid] = r.get("selectedOption", 1)  # default No

    # Score enablement (E1-E5)
    e_codes = list(TEACHER_ENABLEMENT_CODES.keys())
    e_qids = [TEACHER_ENABLEMENT_CODES[c]["question_id"] for c in e_codes]
    enablement_items = {}
    for code, qid in zip(e_codes, e_qids):
        enablement_items[code] = _binary_value(resp_map.get(qid, 1))

    # Score routines (R1-R5)
    r_codes = list(LEADERSHIP_ROUTINE_CODES.keys())
    r_qids = [LEADERSHIP_ROUTINE_CODES[c]["question_id"] for c in r_codes]
    routine_items = {}
    for code, qid in zip(r_codes, r_qids):
        routine_items[code] = _binary_value(resp_map.get(qid, 1))

    # Compute indices
    enablement_sum = sum(enablement_items.values())
    routine_sum = sum(routine_items.values())

    enablement_index = enablement_sum / 5
    routine_index = routine_sum / 5

    teacher_enablement = 10 * enablement_index
    leadership_routines = 10 * routine_index
    system_readiness = teacher_enablement + leadership_routines

    # Determine band
    band = "unknown"
    for band_name, (lo, hi) in SRI_INTERPRETATION_BANDS.items():
        if lo <= system_readiness <= hi:
            band = band_name
            break

    return {
        "enablement_items": enablement_items,
        "routine_items": routine_items,
        "enablement_index": enablement_index,
        "routine_index": routine_index,
        "teacher_enablement": teacher_enablement,
        "leadership_routines": leadership_routines,
        "system_readiness": system_readiness,
        "band": band,
    }


def score_branch(attempts):
    """
    Score SRI for a branch from multiple attempts (Principal + VP + AC).
    Aggregates by majority vote per question (Yes if ≥50% say Yes).

    Args:
        attempts: list of attempt dicts, each with 'responses' array

    Returns:
        Same structure as score_single_attempt, plus:
            respondent_count: int
            per_respondent: list of individual scores
    """
    if not attempts:
        return None

    per_respondent = [score_single_attempt(a.get("responses", [])) for a in attempts]

    # Majority vote per question
    all_e_codes = list(TEACHER_ENABLEMENT_CODES.keys())
    all_r_codes = list(LEADERSHIP_ROUTINE_CODES.keys())

    enablement_items = {}
    for code in all_e_codes:
        votes = [pr["enablement_items"][code] for pr in per_respondent]
        enablement_items[code] = 1 if sum(votes) >= len(votes) / 2 else 0

    routine_items = {}
    for code in all_r_codes:
        votes = [pr["routine_items"][code] for pr in per_respondent]
        routine_items[code] = 1 if sum(votes) >= len(votes) / 2 else 0

    enablement_index = sum(enablement_items.values()) / 5
    routine_index = sum(routine_items.values()) / 5
    teacher_enablement = 10 * enablement_index
    leadership_routines = 10 * routine_index
    system_readiness = teacher_enablement + leadership_routines

    band = "unknown"
    for band_name, (lo, hi) in SRI_INTERPRETATION_BANDS.items():
        if lo <= system_readiness <= hi:
            band = band_name
            break

    return {
        "enablement_items": enablement_items,
        "routine_items": routine_items,
        "enablement_index": enablement_index,
        "routine_index": routine_index,
        "teacher_enablement": teacher_enablement,
        "leadership_routines": leadership_routines,
        "system_readiness": system_readiness,
        "band": band,
        "respondent_count": len(per_respondent),
        "per_respondent": per_respondent,
    }
