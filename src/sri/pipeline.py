#!/usr/bin/env python3
"""
SRI Pipeline — orchestrates all three instruments and produces
branch-level SRI output.

Data sources:
  Instrument 1 (System Readiness Audit):
    - data/extracted/constructs/sri_audit.jsonl  (from extract_sri_audit.js)
  Instrument 2 (Parent Validation):
    - NOT YET AVAILABLE — placeholder for future data
  Instrument 3 (SET):
    - data/extracted/intent/             (orientation data)
    - data/extracted/baseline/           (practice depth + diagnostic areas)
    - data/extracted/constructs/         (all-constructs for FP mapping)

Outputs:
  output/reports/sri_v2_branch_scores.csv
  output/reports/sri_v2_detail.json
"""

import csv
import json
import os
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)

from src.sri.system_readiness_audit import score_single_attempt, score_branch
from src.sri.parent_validation import score_branch as score_parent_branch
from src.sri.set_computation import (
    compute_set1,
    compute_set2_teacher,
    compute_set2_leader,
    generate_fp_explainers,
    detect_archetypes,
)
from src.sri.constants import (
    FP_NAMES,
    TEACHER_AREAS,
    LEADER_AREAS,
    SRI_INTERPRETATION_BANDS,
)

# Paths
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "output", "reports")
CONSTRUCTS = os.path.join(DATA, "extracted", "constructs")
INTENT = os.path.join(DATA, "extracted", "intent")
BASELINE = os.path.join(DATA, "extracted", "baseline")


def load_sri_audit_data(filepath):
    """Load SRI audit JSONL (from extract_sri_audit.js output)."""
    attempts_by_branch = defaultdict(list)
    if not os.path.exists(filepath):
        print(f"  [WARN] SRI audit file not found: {filepath}")
        return attempts_by_branch

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("=") or line.startswith("SET_") or \
               line.startswith("QUESTION_") or line.startswith("SUBMITTED_"):
                continue
            try:
                record = json.loads(line)
                branch = record.get("branchCode", "UNKNOWN")
                attempts_by_branch[branch].append(record)
            except json.JSONDecodeError:
                continue

    return attempts_by_branch


def load_orientation_data():
    """
    Load teacher and leader orientation FPs from intent data.
    Returns: {branchCode: {"teacher_fps": [...], "leader_fps": [...]}}
    """
    orientation = defaultdict(lambda: {"teacher_fps": [], "leader_fps": []})

    # Parse from all_constructs_raw.txt or intent CSVs
    constructs_file = os.path.join(CONSTRUCTS, "all_constructs_raw.txt")
    if not os.path.exists(constructs_file):
        print(f"  [WARN] Constructs file not found: {constructs_file}")
        return orientation

    # The all_constructs extraction contains FP orientation per user per branch
    # Format varies — attempt to parse JSONL lines
    with open(constructs_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                branch = record.get("branchCode", "")
                role = record.get("role", "").lower()
                dominant_fp = record.get("dominantFP", record.get("dominant_fp", ""))
                if not branch or not dominant_fp:
                    continue
                if "teacher" in role:
                    orientation[branch]["teacher_fps"].append(dominant_fp)
                elif "leader" in role:
                    orientation[branch]["leader_fps"].append(dominant_fp)
            except json.JSONDecodeError:
                continue

    return orientation


def load_practice_depth_data():
    """
    Load teacher practice depth from baseline data.
    Returns: {branchCode: {userId: {"fp": "FP2", "depth": 2.5}}}
    """
    depth_data = defaultdict(dict)

    # Parse from baseline CSVs or constructs
    for fname in ["base001_teacher_english.csv", "base003_teacher_marathi.csv"]:
        fpath = os.path.join(BASELINE, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                branch = row.get("branchCode", "")
                uid = row.get("userTempId", "")
                fp = row.get("dominantFP", row.get("dominant_fp", ""))
                depth_str = row.get("depth", row.get("practiceDepth", "0"))
                try:
                    depth = float(depth_str)
                except (ValueError, TypeError):
                    depth = 0.0
                if branch and uid:
                    depth_data[branch][uid] = {"fp": fp, "depth": depth}

    return depth_data


def load_diagnostic_area_scores():
    """
    Load teacher (A1-A4) and leader (B1-B4) diagnostic area scores.
    Returns: {branchCode: {"teacher": {A1: {sub: [scores]}}, "leader": {B1: ...}}}
    """
    area_data = defaultdict(lambda: {
        "teacher": {a: {s: [] for s in TEACHER_AREAS[a]["subareas"]} for a in TEACHER_AREAS},
        "leader": {b: {s: [] for s in LEADER_AREAS[b]["subareas"]} for b in LEADER_AREAS},
    })

    # This data comes from baseline responses parsed through area sub-scores
    # The exact parsing depends on how the baseline CSVs encode area scores
    # For now, try to parse from constructs data
    constructs_file = os.path.join(CONSTRUCTS, "all_constructs_raw.txt")
    if not os.path.exists(constructs_file):
        return area_data

    with open(constructs_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                branch = record.get("branchCode", "")
                role = record.get("role", "").lower()
                areas = record.get("areaScores", {})
                if not branch or not areas:
                    continue

                if "teacher" in role:
                    for area_code in TEACHER_AREAS:
                        area_scores = areas.get(area_code, {})
                        for sub in TEACHER_AREAS[area_code]["subareas"]:
                            val = area_scores.get(sub)
                            if val is not None:
                                area_data[branch]["teacher"][area_code][sub].append(float(val))
                elif "leader" in role:
                    for area_code in LEADER_AREAS:
                        area_scores = areas.get(area_code, {})
                        for sub in LEADER_AREAS[area_code]["subareas"]:
                            val = area_scores.get(sub)
                            if val is not None:
                                area_data[branch]["leader"][area_code][sub].append(float(val))
            except (json.JSONDecodeError, ValueError):
                continue

    return area_data


def run_pipeline():
    """Execute the full SRI pipeline."""
    print("=" * 60)
    print("SRI Pipeline v2 — System Readiness Index")
    print("=" * 60)

    # ── Instrument 1: System Readiness Audit ──
    print("\n[1/3] System Readiness Audit (SRI001)...")
    sri_file = os.path.join(CONSTRUCTS, "sri_audit.jsonl")
    sri_by_branch = load_sri_audit_data(sri_file)
    print(f"  Loaded {sum(len(v) for v in sri_by_branch.values())} attempts across {len(sri_by_branch)} branches")

    sri_scores = {}
    for branch, attempts in sri_by_branch.items():
        result = score_branch(attempts)
        if result:
            sri_scores[branch] = result

    # ── Instrument 2: Parent Validation ──
    print("\n[2/3] Parent Validation Signal...")
    print("  [SKIP] No parent validation data available yet")
    parent_scores = {}

    # ── Instrument 3: SET ──
    print("\n[3/3] SET Computation...")

    # Load data
    orientation = load_orientation_data()
    depth_data = load_practice_depth_data()
    area_data = load_diagnostic_area_scores()

    all_branches = sorted(set(
        list(sri_scores.keys()) +
        list(orientation.keys()) +
        list(depth_data.keys())
    ))
    print(f"  Branches with any data: {len(all_branches)}")

    set_results = {}
    for branch in all_branches:
        ori = orientation.get(branch, {"teacher_fps": [], "leader_fps": []})
        depths = depth_data.get(branch, {})
        areas = area_data.get(branch, {
            "teacher": {a: {s: [] for s in TEACHER_AREAS[a]["subareas"]} for a in TEACHER_AREAS},
            "leader": {b: {s: [] for s in LEADER_AREAS[b]["subareas"]} for b in LEADER_AREAS},
        })

        if not ori["teacher_fps"] and not ori["leader_fps"]:
            continue

        # SET1
        set1 = compute_set1(ori["leader_fps"], ori["teacher_fps"], depths)

        # SET2 Teacher
        set2_teacher = compute_set2_teacher(areas["teacher"])

        # SET2 Leader
        set2_leader = compute_set2_leader(areas["leader"])

        # Explainers
        explainers = generate_fp_explainers(set1, set2_teacher, set2_leader)

        # Archetypes
        archetypes = detect_archetypes(set1, set2_teacher, set2_leader)

        set_results[branch] = {
            "set1": set1,
            "set2_teacher": set2_teacher,
            "set2_leader": set2_leader,
            "explainers": explainers,
            "archetypes": archetypes,
        }

    print(f"  SET computed for {len(set_results)} branches")

    # ── Output ──
    print("\n[OUTPUT] Writing results...")
    os.makedirs(OUT, exist_ok=True)

    # CSV summary
    csv_path = os.path.join(OUT, "sri_v2_branch_scores.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "branchCode",
            # Instrument 1
            "sri_teacher_enablement", "sri_leadership_routines",
            "sri_system_readiness", "sri_band", "sri_respondents",
            # Instrument 2
            "parent_readiness", "parent_band", "parent_respondents",
            # SET1
            "dominant_fp_teacher", "dominant_fp_leader",
            # SET2 Teacher areas
            "A1_mean", "A2_mean", "A3_mean", "A4_mean",
            # SET2 Leader areas
            "B1_mean", "B2_mean", "B3_mean", "B4_mean",
            # Archetype
            "primary_archetype", "confidence",
        ])

        for branch in sorted(all_branches):
            sri = sri_scores.get(branch, {})
            parent = parent_scores.get(branch, {})
            sset = set_results.get(branch, {})
            set1 = sset.get("set1", {})
            set2t = sset.get("set2_teacher", {})
            set2l = sset.get("set2_leader", {})
            arch = sset.get("archetypes", {})

            writer.writerow([
                branch,
                # Instrument 1
                round(sri.get("teacher_enablement", 0), 1),
                round(sri.get("leadership_routines", 0), 1),
                round(sri.get("system_readiness", 0), 1),
                sri.get("band", "no_data"),
                sri.get("respondent_count", 0),
                # Instrument 2
                round(parent.get("parent_readiness", 0), 1),
                parent.get("band", "no_data"),
                parent.get("respondent_count", 0),
                # SET1
                set1.get("dominant_fp_teacher", ""),
                set1.get("dominant_fp_leader", ""),
                # SET2 Teacher
                round(set2t.get("area_means", {}).get("A1", 0), 2),
                round(set2t.get("area_means", {}).get("A2", 0), 2),
                round(set2t.get("area_means", {}).get("A3", 0), 2),
                round(set2t.get("area_means", {}).get("A4", 0), 2),
                # SET2 Leader
                round(set2l.get("area_means", {}).get("B1", 0), 2),
                round(set2l.get("area_means", {}).get("B2", 0), 2),
                round(set2l.get("area_means", {}).get("B3", 0), 2),
                round(set2l.get("area_means", {}).get("B4", 0), 2),
                # Archetype
                arch.get("primary", "none"),
                arch.get("confidence", "low"),
            ])

    print(f"  CSV: {csv_path}")

    # Full JSON detail
    json_path = os.path.join(OUT, "sri_v2_detail.json")
    detail = {}
    for branch in sorted(all_branches):
        detail[branch] = {
            "system_readiness_audit": _serialize(sri_scores.get(branch, {})),
            "parent_validation": _serialize(parent_scores.get(branch, {})),
            "set": _serialize(set_results.get(branch, {})),
        }

    with open(json_path, "w") as f:
        json.dump(detail, f, indent=2, default=str)

    print(f"  JSON: {json_path}")
    print(f"\nDone. {len(all_branches)} branches processed.")


def _serialize(obj):
    """Make nested dicts JSON-serializable (drop lambda, etc.)."""
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    if callable(obj):
        return str(obj)
    return obj


if __name__ == "__main__":
    run_pipeline()
