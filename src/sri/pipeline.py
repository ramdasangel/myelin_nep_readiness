#!/usr/bin/env python3
"""
SRI Pipeline — orchestrates all three instruments and produces
branch-level SRI output.

Data sources (reads existing extracted CSVs directly):
  Instrument 1 (System Readiness Audit):
    - data/extracted/constructs/sri_audit.jsonl  (from extract_sri_audit.js)
  Instrument 2 (Parent Validation):
    - NOT YET AVAILABLE — placeholder for future data
  Instrument 3 (SET):
    - data/extracted/intent/intent_*_responses.csv   (orientation → FP)
    - data/extracted/baseline/base00*_*.csv           (depth + diagnostic areas)

Outputs:
  output/reports/sri_v2_branch_scores.csv
  output/reports/sri_v2_detail.json
"""

import csv
import json
import os
import re
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

# Goal → FP mapping (from compute_sri_scores.py, covers EN + MR)
GOAL_TO_FP = {
    # English teacher
    "Each Child is Unique": "FP1",
    "Competency-Based Learning": "FP2",
    "Teacher Upskilling": "FP3",
    "Diagnosing Learning Levels": "FP4",
    "Parent–Teacher Collaboration": "FP5",
    "Parent-Teacher Collaboration": "FP5",
    # Marathi teacher
    "प्रत्येक मूल वेगळे आहे": "FP1",
    "क्षमताधिष्ठित अध्ययन": "FP2",
    "क्षमताधिष्टित अध्ययन": "FP2",
    "शिक्षक कौशल्यवृद्धी": "FP3",
    "शिक्षक कौशल्यवृध्दी": "FP3",
    "अध्ययन स्तरांचे निदान": "FP4",
    "पालक - शिक्षक सहयोग": "FP5",
    "पालक -शिक्षक सहयोग": "FP5",
    "पालक - शिक्षक सहभागीता": "FP5",
    # English leader
    "Learning Progress Monitoring": "FP1",
    "Student Engagement": "FP1",
    "Understanding Learners": "FP1",
    "Classroom Observation": "FP2",
    "Activity Design": "FP2",
    "Lesson Planning": "FP2",
    "Task Rigor": "FP2",
    "Teacher Support": "FP3",
    "Teacher Coaching": "FP3",
    "Innovation in Teaching": "FP3",
    "Teacher Development": "FP3",
    "Team Leadership": "FP3",
    "School Improvement": "FP3",
    "Data Analysis": "FP4",
    "Instructional Review": "FP4",
    "Learning Data Analysis": "FP4",
    "Parent Engagement": "FP5",
    "Parent Communication": "FP5",
    "School Communication": "FP5",
}

# Sub-area → Area mapping for baseline questions (teacher)
# Teacher baseline questionGoal values map to A1-A4 sub-areas
SUBAREA_TO_TEACHER_AREA = {}
for area_code, area_def in TEACHER_AREAS.items():
    for sub in area_def["subareas"]:
        SUBAREA_TO_TEACHER_AREA[sub.lower()] = (area_code, sub)

# Additional mappings for how goals appear in CSVs
_TEACHER_GOAL_ALIASES = {
    "access": ("A1", "Access"),
    "usability": ("A1", "Usability"),
    "follow-through": ("A1", "FollowThrough"),
    "follow through": ("A1", "FollowThrough"),
    "collective use": ("A1", "CollectiveUse"),
    "student clarity": ("A1", "StudentClarity"),
    "structure": ("A2", "Structure"),
    "safety": ("A2", "Safety"),
    "peer learning": ("A2", "PeerLearning"),
    "experimentation": ("A2", "Experimentation"),
    "growth culture": ("A2", "GrowthCulture"),
    "understanding": ("A3", "Understanding"),
    "clarity": ("A3", "Clarity"),
    "time": ("A3", "Time"),
    "use": ("A3", "Use"),
    "student role": ("A3", "StudentRole"),
    "communication": ("A4", "Communication"),
    "guidance": ("A4", "Guidance"),
    "facilitation": ("A4", "Facilitation"),
    "recognition": ("A4", "Recognition"),
    # Common Marathi mappings in the CSVs
    "सुलभता": ("A1", "Access"),
    "उपयुक्तता": ("A1", "Usability"),
    "कृतिशीलता": ("A1", "FollowThrough"),
    "सामूहिक वापर": ("A1", "CollectiveUse"),
    "विद्यार्थी स्पष्टता": ("A1", "StudentClarity"),
}
SUBAREA_TO_TEACHER_AREA.update(_TEACHER_GOAL_ALIASES)

# Leader baseline questionGoal → B1-B4 sub-areas
SUBAREA_TO_LEADER_AREA = {
    "ownership clarity": ("B1", "OwnershipClarity"),
    "ownership": ("B1", "OwnershipClarity"),
    "translation to action": ("B1", "TranslationToAction"),
    "translation": ("B1", "TranslationToAction"),
    "responsibility distribution": ("B1", "ResponsibilityDistribution"),
    "distribution": ("B1", "ResponsibilityDistribution"),
    "review practice": ("B2", "ReviewPractice"),
    "review practices": ("B2", "ReviewPractice"),
    "decision use": ("B2", "DecisionUse"),
    "change support": ("B2", "ChangeSupport"),
    "support for change": ("B2", "ChangeSupport"),
    "plc regularity": ("B3", "PLCRegularity"),
    "safety": ("B3", "Safety"),
    "experimentation protection": ("B3", "ExperimentationProtection"),
    "experimentation": ("B3", "ExperimentationProtection"),
    "purpose clarity": ("B4", "PurposeClarity"),
    "parent orientation": ("B4", "ParentOrientation"),
    "teacher support": ("B4", "TeacherSupport"),
}

# Likert reverse: selectedOption 0=SA(4), 1=A(3), 2=D(2), 3=SD(1)
LIKERT_REVERSE = {0: 4, 1: 3, 2: 2, 3: 1}

# Exclude dev/test branch codes
DEV_BRANCHES = {"m56b0", "m942e"}


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
                if branch in DEV_BRANCHES:
                    continue
                attempts_by_branch[branch].append(record)
            except json.JSONDecodeError:
                continue

    return attempts_by_branch


def load_orientation_data():
    """
    Load teacher and leader orientation FPs from intent response CSVs.
    Reads: intent_teacher_english_responses.csv, intent_teacher_marathi_responses.csv,
           intent_leader_english_responses.csv, intent_leader_marathi_responses.csv
    Returns: {branchCode: {"teacher_fps": [...], "leader_fps": [...]}}
    """
    orientation = defaultdict(lambda: {"teacher_fps": [], "leader_fps": []})

    intent_files = [
        "intent_teacher_english_responses.csv",
        "intent_teacher_marathi_responses.csv",
        "intent_leader_english_responses.csv",
        "intent_leader_marathi_responses.csv",
    ]

    # Collect per-user dominant FP (most frequent goal→FP across responses)
    user_fp_votes = defaultdict(lambda: defaultdict(int))  # userId → {FP: count}
    user_meta = {}  # userId → {branchCode, role}

    for fname in intent_files:
        fpath = os.path.join(INTENT, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                branch = row.get("branchCode", "")
                if not branch or branch in DEV_BRANCHES:
                    continue
                uid = row.get("userId", "")
                role = row.get("role", "").lower()
                goal = row.get("goal", "")
                fp = GOAL_TO_FP.get(goal)
                if not fp or not uid:
                    continue

                user_fp_votes[uid][fp] += 1
                if uid not in user_meta:
                    user_meta[uid] = {"branchCode": branch, "role": role}

    # Determine dominant FP per user
    for uid, fp_counts in user_fp_votes.items():
        meta = user_meta[uid]
        branch = meta["branchCode"]
        role = meta["role"]
        dominant_fp = max(fp_counts, key=fp_counts.get)

        if "teacher" in role:
            orientation[branch]["teacher_fps"].append(dominant_fp)
        elif "leader" in role:
            orientation[branch]["leader_fps"].append(dominant_fp)

    return orientation


def load_baseline_data():
    """
    Load practice depth and diagnostic area scores from baseline CSVs.
    The CSVs have one row per question per user, with columns:
      userId, branchCode, roleName, questionGoal, selectedOption, depthLevel, fpLevel

    Returns tuple:
      depth_data: {branchCode: {userId: {"fp": "FP2", "depth": avg}}}
      area_data: {branchCode: {"teacher": {A1: {sub: [scores]}}, "leader": {B1: ...}}}
    """
    depth_data = defaultdict(dict)
    area_data = defaultdict(lambda: {
        "teacher": {a: {s: [] for s in TEACHER_AREAS[a]["subareas"]} for a in TEACHER_AREAS},
        "leader": {b: {s: [] for s in LEADER_AREAS[b]["subareas"]} for b in LEADER_AREAS},
    })

    baseline_files = {
        "base001_teacher_english.csv": "teacher",
        "base003_teacher_marathi.csv": "teacher",
        "base002_leader_english.csv": "leader",
        "base004_leader_marathi.csv": "leader",
    }

    # Collect per-user depth values and area scores
    user_depths = defaultdict(list)  # userId → [depth values]
    user_fp_votes = defaultdict(lambda: defaultdict(int))  # userId → {FP: count}
    user_branch = {}  # userId → branchCode

    for fname, audience in baseline_files.items():
        fpath = os.path.join(BASELINE, fname)
        if not os.path.exists(fpath):
            print(f"  [WARN] Baseline file not found: {fname}")
            continue

        with open(fpath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                branch = row.get("branchCode", "")
                if not branch or branch in DEV_BRANCHES:
                    continue

                uid = row.get("userId", "")
                if not uid:
                    continue

                user_branch[uid] = branch
                goal = row.get("questionGoal", "").strip()
                goal_lower = goal.lower()

                # Selected option → Likert score (4=SA, 3=A, 2=D, 1=SD)
                try:
                    sel = int(row.get("selectedOption", 2))
                except (ValueError, TypeError):
                    sel = 2
                likert = LIKERT_REVERSE.get(sel, 2)

                # Depth level (if present in baseline data)
                depth_str = row.get("depthLevel", "")
                if depth_str:
                    try:
                        depth_val = float(depth_str)
                        user_depths[uid].append(depth_val)
                    except (ValueError, TypeError):
                        pass

                # FP level (if present)
                fp_str = row.get("fpLevel", "")
                if fp_str:
                    fp = GOAL_TO_FP.get(fp_str, fp_str)
                    if fp.startswith("FP"):
                        user_fp_votes[uid][fp] += 1

                # Map questionGoal to area/sub-area
                if audience == "teacher":
                    mapping = SUBAREA_TO_TEACHER_AREA.get(goal_lower)
                    if mapping:
                        area_code, subarea = mapping
                        area_data[branch]["teacher"][area_code][subarea].append(likert)
                elif audience == "leader":
                    mapping = SUBAREA_TO_LEADER_AREA.get(goal_lower)
                    if mapping:
                        area_code, subarea = mapping
                        area_data[branch]["leader"][area_code][subarea].append(likert)

    # Compute per-user average depth and dominant FP
    for uid, depths in user_depths.items():
        branch = user_branch.get(uid, "")
        if not branch:
            continue
        avg_depth = sum(depths) / len(depths)
        fp_counts = user_fp_votes.get(uid, {})
        dominant_fp = max(fp_counts, key=fp_counts.get) if fp_counts else ""
        depth_data[branch][uid] = {"fp": dominant_fp, "depth": avg_depth}

    return depth_data, area_data


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
    print("  Loading orientation from intent CSVs...")
    orientation = load_orientation_data()
    print(f"  Orientation: {sum(len(v['teacher_fps']) for v in orientation.values())} teachers, "
          f"{sum(len(v['leader_fps']) for v in orientation.values())} leaders across {len(orientation)} branches")

    print("  Loading baseline data (depth + diagnostic areas)...")
    depth_data, area_data = load_baseline_data()
    print(f"  Depth data: {sum(len(v) for v in depth_data.values())} users across {len(depth_data)} branches")

    # Collect area coverage stats
    area_count = 0
    for branch, ad in area_data.items():
        for area in ad["teacher"].values():
            for sub_scores in area.values():
                if sub_scores:
                    area_count += 1
                    break
    print(f"  Area scores: {area_count} branch-area combinations with data")

    all_branches = sorted(set(
        list(sri_scores.keys()) +
        list(orientation.keys()) +
        list(depth_data.keys())
    ))
    # Filter out dev branches
    all_branches = [b for b in all_branches if b not in DEV_BRANCHES and b]
    print(f"  Total branches with any data: {len(all_branches)}")

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
            "teacher_count", "leader_count",
            # SET2 Teacher areas
            "A1_mean", "A1_band", "A2_mean", "A2_band",
            "A3_mean", "A3_band", "A4_mean", "A4_band",
            # SET2 Leader areas
            "B1_mean", "B1_band", "B2_mean", "B2_band",
            "B3_mean", "B3_band", "B4_mean", "B4_band",
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
            ori = orientation.get(branch, {"teacher_fps": [], "leader_fps": []})

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
                len(ori["teacher_fps"]),
                len(ori["leader_fps"]),
                # SET2 Teacher
                round(set2t.get("area_means", {}).get("A1", 0), 2),
                set2t.get("area_bands", {}).get("A1", ""),
                round(set2t.get("area_means", {}).get("A2", 0), 2),
                set2t.get("area_bands", {}).get("A2", ""),
                round(set2t.get("area_means", {}).get("A3", 0), 2),
                set2t.get("area_bands", {}).get("A3", ""),
                round(set2t.get("area_means", {}).get("A4", 0), 2),
                set2t.get("area_bands", {}).get("A4", ""),
                # SET2 Leader
                round(set2l.get("area_means", {}).get("B1", 0), 2),
                set2l.get("area_bands", {}).get("B1", ""),
                round(set2l.get("area_means", {}).get("B2", 0), 2),
                set2l.get("area_bands", {}).get("B2", ""),
                round(set2l.get("area_means", {}).get("B3", 0), 2),
                set2l.get("area_bands", {}).get("B3", ""),
                round(set2l.get("area_means", {}).get("B4", 0), 2),
                set2l.get("area_bands", {}).get("B4", ""),
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
