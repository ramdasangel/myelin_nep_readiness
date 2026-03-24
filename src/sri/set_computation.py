"""
Instrument 3: SET — Structured Explanation of Translation

SET is a disciplined reading grammar, NOT a score.
It explains how NEP intent translates (or fails to translate) into
classroom practice under real school conditions.

Two layers:
  SET1: Orientation Alignment × Practice Depth  → WHERE to look
  SET2: Practice Depth × Diagnostic Areas       → WHY it looks that way

All outputs are cluster/school level — never individual.
"""

from collections import defaultdict
from .constants import (
    ALIGNMENT_STATES,
    AREA_BANDS,
    CORE_ARCHETYPES,
    DEPTH_BANDS,
    DEPTH_NUMERIC,
    FP_ARCHETYPES,
    FP_LEADER_AREA_LINKS,
    FP_NAMES,
    FP_TEACHER_AREA_LINKS,
    LEADER_AREAS,
    ORIENTATION_BANDS,
    TEACHER_AREAS,
    TENSION_ARCHETYPES,
)


# ═══════════════════════════════════════════════════════════════════
#  SET1: Orientation Alignment × Practice Depth
# ═══════════════════════════════════════════════════════════════════

def _band_orientation(p):
    """Classify orientation proportion into High/Medium/Low."""
    for band, fn in ORIENTATION_BANDS.items():
        if fn(p):
            return band
    return "low"


def _band_depth(d):
    """Classify average depth into Low/Mid/High."""
    for band, fn in DEPTH_BANDS.items():
        if fn(d):
            return band
    return "low"


def compute_set1(leader_fps, teacher_fps, teacher_depths):
    """
    Compute SET1 alignment analysis.

    Args:
        leader_fps: list of FP strings (one per leader), e.g. ["FP1", "FP2", ...]
        teacher_fps: list of FP strings (one per teacher)
        teacher_depths: dict of {teacher_id: {"fp": "FP2", "depth": 2.5}}

    Returns:
        dict with:
            leader_orientation_dist: {FP1: pL, FP2: pL, ...}
            teacher_orientation_dist: {FP1: pT, ...}
            teacher_depth_by_fp: {FP1: avg_depth, ...}
            alignment_gap_by_fp: {FP1: pT - pL, ...}
            alignment_state_by_fp: {FP1: state, ...}
            dominant_fp_leader: str
            dominant_fp_teacher: str
    """
    fp_keys = list(FP_NAMES.keys())

    # Leader orientation distribution
    leader_total = len(leader_fps) if leader_fps else 1
    leader_counts = defaultdict(int)
    for fp in leader_fps:
        leader_counts[fp] += 1
    leader_dist = {fp: leader_counts[fp] / leader_total for fp in fp_keys}

    # Teacher orientation distribution
    teacher_total = len(teacher_fps) if teacher_fps else 1
    teacher_counts = defaultdict(int)
    for fp in teacher_fps:
        teacher_counts[fp] += 1
    teacher_dist = {fp: teacher_counts[fp] / teacher_total for fp in fp_keys}

    # Teacher depth by FP
    depth_by_fp = defaultdict(list)
    for tid, info in teacher_depths.items():
        fp = info.get("fp")
        d = info.get("depth", 0)
        if fp:
            depth_by_fp[fp].append(d)

    teacher_depth_by_fp = {}
    for fp in fp_keys:
        vals = depth_by_fp.get(fp, [])
        teacher_depth_by_fp[fp] = sum(vals) / len(vals) if vals else 0.0

    # Alignment gap
    alignment_gap = {fp: teacher_dist[fp] - leader_dist[fp] for fp in fp_keys}

    # Alignment state per FP
    alignment_state = {}
    for fp in fp_keys:
        l_band = _band_orientation(leader_dist[fp])
        t_band = _band_orientation(teacher_dist[fp])
        d_band = _band_depth(teacher_depth_by_fp[fp])

        if l_band == "high" and t_band == "high" and d_band == "low":
            alignment_state[fp] = "intent_high_translation_low"
        elif t_band == "high" and l_band == "low":
            alignment_state[fp] = "teacher_led_intent"
        elif l_band == "high" and t_band == "low":
            alignment_state[fp] = "leader_led_intent"
        elif l_band == "low" and t_band == "low":
            alignment_state[fp] = "low_attention_zone"
        elif l_band in ("high", "medium") and t_band in ("high", "medium") and d_band == "high":
            alignment_state[fp] = "intent_translation_aligned"
        else:
            alignment_state[fp] = "emerging"

    # Dominant FPs
    dominant_leader = max(fp_keys, key=lambda fp: leader_dist[fp])
    dominant_teacher = max(fp_keys, key=lambda fp: teacher_dist[fp])

    return {
        "leader_orientation_dist": leader_dist,
        "teacher_orientation_dist": teacher_dist,
        "teacher_depth_by_fp": teacher_depth_by_fp,
        "alignment_gap_by_fp": alignment_gap,
        "alignment_state_by_fp": alignment_state,
        "dominant_fp_leader": dominant_leader,
        "dominant_fp_teacher": dominant_teacher,
    }


# ═══════════════════════════════════════════════════════════════════
#  SET2: Practice Depth × Diagnostic Areas (Teacher A1-A4, Leader B1-B4)
# ═══════════════════════════════════════════════════════════════════

def _band_area(score):
    """Classify area/sub-area score into Low/Mid/High."""
    for band, fn in AREA_BANDS.items():
        if fn(score):
            return band
    return "mid"


def compute_set2_teacher(teacher_area_scores):
    """
    Compute SET2 teacher-side analysis.

    Args:
        teacher_area_scores: dict of {
            "A1": {"Access": [scores], "Usability": [scores], ...},
            "A2": {...}, "A3": {...}, "A4": {...}
        }
        Each score list contains per-teacher Likert values (1-4).

    Returns:
        dict with:
            area_means: {A1: mean, A2: mean, ...}
            area_bands: {A1: "low"|"mid"|"high", ...}
            subarea_means: {A1_Access: mean, A1_Usability: mean, ...}
            subarea_bands: {A1_Access: "low", ...}
    """
    area_means = {}
    area_bands = {}
    subarea_means = {}
    subarea_bands = {}

    for area_code, area_def in TEACHER_AREAS.items():
        all_scores = []
        raw = teacher_area_scores.get(area_code, {})

        for sub in area_def["subareas"]:
            values = raw.get(sub, [])
            key = f"{area_code}_{sub}"
            if values:
                m = sum(values) / len(values)
                subarea_means[key] = m
                subarea_bands[key] = _band_area(m)
                all_scores.extend(values)
            else:
                subarea_means[key] = 0.0
                subarea_bands[key] = "low"

        if all_scores:
            am = sum(all_scores) / len(all_scores)
            area_means[area_code] = am
            area_bands[area_code] = _band_area(am)
        else:
            area_means[area_code] = 0.0
            area_bands[area_code] = "low"

    return {
        "area_means": area_means,
        "area_bands": area_bands,
        "subarea_means": subarea_means,
        "subarea_bands": subarea_bands,
    }


def compute_set2_leader(leader_area_scores):
    """
    Compute SET2 leader-side analysis.

    Args:
        leader_area_scores: dict of {
            "B1": {"OwnershipClarity": [scores], ...},
            "B2": {...}, "B3": {...}, "B4": {...}
        }

    Returns:
        Same structure as compute_set2_teacher but with B1-B4.
    """
    area_means = {}
    area_bands = {}
    subarea_means = {}
    subarea_bands = {}

    for area_code, area_def in LEADER_AREAS.items():
        all_scores = []
        raw = leader_area_scores.get(area_code, {})

        for sub in area_def["subareas"]:
            values = raw.get(sub, [])
            key = f"{area_code}_{sub}"
            if values:
                m = sum(values) / len(values)
                subarea_means[key] = m
                subarea_bands[key] = _band_area(m)
                all_scores.extend(values)
            else:
                subarea_means[key] = 0.0
                subarea_bands[key] = "low"

        if all_scores:
            am = sum(all_scores) / len(all_scores)
            area_means[area_code] = am
            area_bands[area_code] = _band_area(am)
        else:
            area_means[area_code] = 0.0
            area_bands[area_code] = "low"

    return {
        "area_means": area_means,
        "area_bands": area_bands,
        "subarea_means": subarea_means,
        "subarea_bands": subarea_bands,
    }


def generate_fp_explainers(set1_result, set2_teacher, set2_leader):
    """
    Generate FP-level explainability from SET2 areas.

    Args:
        set1_result: output of compute_set1
        set2_teacher: output of compute_set2_teacher
        set2_leader: output of compute_set2_leader

    Returns:
        dict of {FP1: {
            teacher_areas: {A1: {mean, band, subareas: {...}}},
            leader_areas: {B2: {...}},
            condition_flags: ["low_access", "low_safety", ...],
        }, ...}
    """
    explainers = {}
    for fp in FP_NAMES:
        teacher_links = FP_TEACHER_AREA_LINKS.get(fp, [])
        leader_links = FP_LEADER_AREA_LINKS.get(fp, [])

        t_areas = {}
        for a in teacher_links:
            t_areas[a] = {
                "mean": set2_teacher["area_means"].get(a, 0),
                "band": set2_teacher["area_bands"].get(a, "low"),
            }

        l_areas = {}
        for b in leader_links:
            l_areas[b] = {
                "mean": set2_leader["area_means"].get(b, 0),
                "band": set2_leader["area_bands"].get(b, "low"),
            }

        # Collect condition flags
        flags = []
        for a, info in t_areas.items():
            if info["band"] == "low":
                area_def = TEACHER_AREAS.get(a, {})
                for sub in area_def.get("subareas", []):
                    key = f"{a}_{sub}"
                    if set2_teacher["subarea_bands"].get(key) == "low":
                        flags.append(f"low_{sub.lower()}")

        for b, info in l_areas.items():
            if info["band"] == "low":
                area_def = LEADER_AREAS.get(b, {})
                for sub in area_def.get("subareas", []):
                    key = f"{b}_{sub}"
                    if set2_leader["subarea_bands"].get(key) == "low":
                        flags.append(f"low_{sub.lower()}")

        explainers[fp] = {
            "teacher_areas": t_areas,
            "leader_areas": l_areas,
            "condition_flags": flags,
        }

    return explainers


# ═══════════════════════════════════════════════════════════════════
#  Archetype Detection
# ═══════════════════════════════════════════════════════════════════

def detect_archetypes(set1_result, set2_teacher, set2_leader):
    """
    Detect SET archetypes from SET1 + SET2 results.

    Returns:
        dict with:
            primary: archetype ID or None
            secondary: list of archetype IDs
            fp_archetypes: list of matched FP-specific archetypes
            tension_archetypes: list of matched tension archetypes
            confidence: "low" | "medium" | "high"
    """
    t_bands = set2_teacher["area_bands"]
    l_bands = set2_leader["area_bands"]

    # Check core archetypes
    matched_core = []
    for arch_id, arch in CORE_ARCHETYPES.items():
        # Check SET1 state — at least one FP must match
        state_match = any(
            s == arch["set1_state"]
            for s in set1_result["alignment_state_by_fp"].values()
        )
        if not state_match:
            continue

        # Check teacher conditions
        t_match = all(
            t_bands.get(area) == band
            for area, band in arch["teacher_conditions"].items()
        )

        # Check leader conditions
        l_match = all(
            l_bands.get(area) == band
            for area, band in arch["leader_conditions"].items()
        )

        if t_match and l_match:
            matched_core.append(arch_id)

    # Check FP-specific archetypes
    matched_fp = []
    for arch_id, arch in FP_ARCHETYPES.items():
        conds = arch["conditions"]
        match = all(
            t_bands.get(a) == b or l_bands.get(a) == b
            for a, b in conds.items()
        )
        if match:
            matched_fp.append(arch_id)

    # Check tension archetypes
    matched_tension = []
    for arch_id, arch in TENSION_ARCHETYPES.items():
        t_match = all(
            t_bands.get(a) == b for a, b in arch["teacher_conditions"].items()
        )
        l_match = all(
            l_bands.get(a) == b for a, b in arch["leader_conditions"].items()
        )
        if t_match and l_match:
            matched_tension.append(arch_id)

    # Confidence
    total_matches = len(matched_core) + len(matched_fp) + len(matched_tension)
    if total_matches >= 3:
        confidence = "high"
    elif total_matches >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "primary": matched_core[0] if matched_core else None,
        "secondary": matched_core[1:],
        "fp_archetypes": matched_fp,
        "tension_archetypes": matched_tension,
        "confidence": confidence,
    }


def generate_set_sentence(fp, depth_band, area_code, subarea_flags):
    """
    Generate a canonical SET interpretation sentence.

    Template:
      Given [FP orientation], and observed practice depth at [Dx],
      translation is shaped by [Area + sub-areas], indicating that
      [condition], rather than intent, is the limiting factor.

    Args:
        fp: str, e.g. "FP2"
        depth_band: str, "low" | "mid" | "high"
        area_code: str, e.g. "A3"
        subarea_flags: list of low sub-area names

    Returns:
        str — the canonical sentence
    """
    fp_name = FP_NAMES.get(fp, fp)
    depth_map = {"low": "D1-D2", "mid": "D2-D3", "high": "D3-D4"}
    depth_label = depth_map.get(depth_band, depth_band)

    area_name = TEACHER_AREAS.get(area_code, LEADER_AREAS.get(area_code, {})).get("name", area_code)

    if subarea_flags:
        conditions = " and ".join(f"low {f}" for f in subarea_flags)
    else:
        conditions = f"constraints in {area_name}"

    return (
        f"Given high {fp_name} orientation and practice depth at {depth_label}, "
        f"translation is shaped by {conditions} in {area_name}, indicating that "
        f"structural conditions—not teacher intent—are the limiting factor."
    )
