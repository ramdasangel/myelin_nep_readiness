#!/usr/bin/env python3
"""
SRI Unified Pipeline — computes all 5 constructs + SET → single JSON.

Merges:
  - src/compute_sri_scores.py (C1-C4 scores)
  - src/sri/pipeline.py (SET + SRI audit)

Output:
  output/reports/sri_unified.json
"""

import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src.compute_sri_scores import (
    compute_c1, compute_c2, compute_c3, compute_c4,
    build_code_to_name, read_csv, safe_int, safe_float,
    TEACHER_GOAL_FP, LEADER_EN_GOAL_FP, EXCLUDED_BRANCH_CODES,
    INTENT_DIR, CONSTRUCTS_DIR, OUT,
)
from src.sri.pipeline import (
    load_sri_audit_data, load_orientation_data, load_baseline_data,
    DEV_BRANCHES, GOAL_TO_FP, LIKERT_REVERSE, SUBAREA_TO_TEACHER_AREA,
    SUBAREA_TO_LEADER_AREA,
)
from src.sri.system_readiness_audit import score_branch as score_sri_audit
from src.sri.set_computation import (
    compute_set1, compute_set2_teacher, compute_set2_leader,
    generate_fp_explainers, detect_archetypes,
)
from src.sri.constants import (
    FP_NAMES, TEACHER_AREAS, LEADER_AREAS,
    TEACHER_ENABLEMENT_CODES, LEADERSHIP_ROUTINE_CODES,
)

FPS = ['FP1', 'FP2', 'FP3', 'FP4', 'FP5']
REPORTS = os.path.join(BASE, 'output', 'reports')


# ═══════════════════════════════════════════════════════════
#  Detail extractors (enrich C1-C4 with intermediate values)
# ═══════════════════════════════════════════════════════════

def compute_c1_detail():
    """C1 with per-branch FP orientation scores, coverage, balance, alignment."""
    teacher_fp = defaultdict(lambda: defaultdict(list))
    leader_fp = defaultdict(lambda: defaultdict(list))
    teacher_counts = defaultdict(int)
    leader_counts = defaultdict(int)

    try:
        LEADER_MR_GOAL_FP = __import__('src.compute_sri_scores', fromlist=['LEADER_MR_GOAL_FP']).LEADER_MR_GOAL_FP
    except (ImportError, AttributeError):
        LEADER_MR_GOAL_FP = LEADER_EN_GOAL_FP

    intent_files = [
        ('intent_teacher_english_responses.csv', 'Teacher', TEACHER_GOAL_FP),
        ('intent_teacher_marathi_responses.csv', 'Teacher', TEACHER_GOAL_FP),
        ('intent_leader_english_responses.csv', 'Leader', LEADER_EN_GOAL_FP),
        ('intent_leader_marathi_responses.csv', 'Leader', LEADER_MR_GOAL_FP),
    ]

    user_seen = defaultdict(set)
    for fn, role, goal_map in intent_files:
        path = os.path.join(INTENT_DIR, fn)
        if not os.path.exists(path):
            continue
        for row in read_csv(path):
            bc = row['branchCode'].strip()
            goal = row['goal'].strip()
            opt = safe_int(row.get('selectedOption', ''), -1)
            uid = row.get('userId', '')
            if opt < 0 or not bc or bc in EXCLUDED_BRANCH_CODES:
                continue
            fp = goal_map.get(goal)
            if not fp:
                continue
            if role == 'Teacher':
                teacher_fp[bc][fp].append(opt)
                if uid and uid not in user_seen[(bc, 'teacher')]:
                    user_seen[(bc, 'teacher')].add(uid)
                    teacher_counts[bc] += 1
            else:
                leader_fp[bc][fp].append(opt)
                if uid and uid not in user_seen[(bc, 'leader')]:
                    user_seen[(bc, 'leader')].add(uid)
                    leader_counts[bc] += 1

    def variance(vec):
        if not vec or all(v == 0 for v in vec):
            return 0.16
        mu = sum(vec) / len(vec)
        return sum((v - mu) ** 2 for v in vec) / len(vec)

    def cosine_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na > 0 and nb > 0 else 0.0

    all_branches = sorted(set(teacher_fp) | set(leader_fp))
    details = {}

    for bc in all_branches:
        t_orientation = {fp: (sum(teacher_fp[bc].get(fp, [])) / (len(teacher_fp[bc].get(fp, [])) * 3.0)
                              if teacher_fp[bc].get(fp) else 0.0) for fp in FPS}
        l_orientation = {fp: (sum(leader_fp[bc].get(fp, [])) / (len(leader_fp[bc].get(fp, [])) * 3.0)
                              if leader_fp[bc].get(fp) else 0.0) for fp in FPS}

        t_vec = [t_orientation[fp] for fp in FPS]
        l_vec = [l_orientation[fp] for fp in FPS]

        tau = 0.10
        t_cov = sum(1 for v in t_vec if v > tau) / 5.0
        l_cov = sum(1 for v in l_vec if v > tau) / 5.0
        t_bal = max(0.0, 1 - variance(t_vec) / 0.16)
        l_bal = max(0.0, 1 - variance(l_vec) / 0.16)
        align = cosine_sim(t_vec, l_vec)

        t_score = t_cov * t_bal * align
        l_score = l_cov * l_bal * align
        c1 = 10 * t_score + 10 * l_score

        details[bc] = {
            "C1": round(c1, 2),
            "teacher_orientation": {fp: round(v, 4) for fp, v in t_orientation.items()},
            "leader_orientation": {fp: round(v, 4) for fp, v in l_orientation.items()},
            "teacher_coverage": round(t_cov, 4),
            "leader_coverage": round(l_cov, 4),
            "teacher_balance": round(t_bal, 4),
            "leader_balance": round(l_bal, 4),
            "alignment": round(align, 4),
            "teacher_score": round(t_score, 4),
            "leader_score": round(l_score, 4),
            "teacher_count": teacher_counts.get(bc, 0),
            "leader_count": leader_counts.get(bc, 0),
        }

    return details


def compute_c2_detail():
    """C2 with per-branch PDDM matrix and per-FP e_norm."""
    NON_OBS = {('FP1', 0), ('FP1', 3), ('FP2', 3)}
    MAX_DEPTH = {'FP1': 2.0, 'FP2': 2.0, 'FP3': 3.0, 'FP4': 3.0, 'FP5': 3.0}

    branch_fp_depth = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for fn in ['intent_teacher_english_responses.csv', 'intent_teacher_marathi_responses.csv']:
        path = os.path.join(INTENT_DIR, fn)
        if not os.path.exists(path):
            continue
        for row in read_csv(path):
            bc = row['branchCode'].strip()
            goal = row['goal'].strip()
            opt = safe_int(row.get('selectedOption', ''), -1)
            if opt < 0 or not bc or bc in EXCLUDED_BRANCH_CODES:
                continue
            fp = TEACHER_GOAL_FP.get(goal)
            if not fp:
                continue
            branch_fp_depth[bc][fp][opt] += 1

    details = {}
    for bc in branch_fp_depth:
        pddm = {}
        e_norm = {}
        covered = 0

        for fp in FPS:
            raw = [branch_fp_depth[bc][fp].get(d, 0) for d in range(4)]
            masked = [0 if (fp, d) in NON_OBS else raw[d] for d in range(4)]
            total = sum(masked)
            pddm[fp] = {"D1": masked[0], "D2": masked[1], "D3": masked[2], "D4": masked[3]}

            if total == 0:
                e_norm[fp] = 0.0
                continue
            covered += 1
            e_depth = sum(d * masked[d] for d in range(4)) / total
            e_norm[fp] = round(min(e_depth / MAX_DEPTH[fp], 1.0), 4)

        cov_fp = covered / 5.0
        mean_e = sum(e_norm.values()) / len([v for v in e_norm.values() if v > 0]) if any(v > 0 for v in e_norm.values()) else 0.0
        depth_eff = cov_fp * mean_e
        c2 = 25 * depth_eff

        details[bc] = {
            "C2": round(c2, 2),
            "pddm": pddm,
            "e_norm": e_norm,
            "coverage_fp": round(cov_fp, 4),
            "mean_e_norm": round(mean_e, 4),
            "depth_effectiveness": round(depth_eff, 4),
        }

    return details


def compute_c3_detail():
    """C3 with per-branch CPD dimensions and user-level CPIs."""
    from src.compute_sri_scores import build_branch_name_to_code
    branch_map = build_branch_name_to_code()
    path = os.path.join(OUT, 'reports', 'mathangle_master.csv')
    if not os.path.exists(path):
        # Try old path
        path = os.path.join(OUT, 'mathangle_master.csv')
    if not os.path.exists(path):
        print("  SKIP: mathangle_master.csv not found")
        return {}

    rows = read_csv(path)
    user_records = []
    max_indecision = 0.0

    for row in rows:
        branch = row.get('Branch', '').strip()
        bc = branch_map.get(branch, '')
        analyze_r = safe_int(row.get('Cog:Analyze (Right)', ''))
        evaluate_r = safe_int(row.get('Cog:Evaluate (Right)', ''))
        cog_total = (safe_int(row.get('Cog:Understand (Total)', ''))
                   + safe_int(row.get('Cog:Apply (Total)', ''))
                   + safe_int(row.get('Cog:Analyze (Total)', ''))
                   + safe_int(row.get('Cog:Evaluate (Total)', '')))
        cpd1 = (analyze_r + evaluate_r) / cog_total if cog_total > 0 else 0.0
        l2_r = safe_int(row.get('Diff:L2 (Right)', ''))
        l2_t = safe_int(row.get('Diff:L2 (Total)', ''))
        l3_r = safe_int(row.get('Diff:L3 (Right)', ''))
        l3_t = safe_int(row.get('Diff:L3 (Total)', ''))
        l2_acc = l2_r / l2_t if l2_t > 0 else 0.0
        l3_acc = l3_r / l3_t if l3_t > 0 else 0.0
        cpd2 = (l2_acc + l3_acc) / 2.0
        indecision = safe_float(row.get('Indecision Score', ''))
        flip_flops = safe_int(row.get('Flip-Flops', ''))
        max_indecision = max(max_indecision, indecision)
        user_records.append({
            'branchCode': bc, 'cpd1': cpd1, 'cpd2': cpd2,
            'indecision': indecision, 'flip_flops': flip_flops, 'total_q': cog_total,
        })

    if max_indecision == 0:
        max_indecision = 1.0

    branch_users = defaultdict(list)
    for u in user_records:
        cpd3 = 1.0 - (u['indecision'] / max_indecision)
        cpd4 = 1.0 - (u['flip_flops'] / u['total_q']) if u['total_q'] > 0 else 1.0
        cpi = (u['cpd1'] + u['cpd2'] + cpd3 + cpd4) / 4.0
        if u['branchCode']:
            branch_users[u['branchCode']].append({
                'cpd1': round(u['cpd1'], 4), 'cpd2': round(u['cpd2'], 4),
                'cpd3': round(cpd3, 4), 'cpd4': round(cpd4, 4), 'cpi': round(cpi, 4),
            })

    details = {}
    for bc, users in branch_users.items():
        cpis = [u['cpi'] for u in users]
        cpi_avg = sum(cpis) / len(cpis)
        cpd_means = {
            'CPD1': round(sum(u['cpd1'] for u in users) / len(users), 4),
            'CPD2': round(sum(u['cpd2'] for u in users) / len(users), 4),
            'CPD3': round(sum(u['cpd3'] for u in users) / len(users), 4),
            'CPD4': round(sum(u['cpd4'] for u in users) / len(users), 4),
        }
        details[bc] = {
            "C3": round(20 * cpi_avg, 2),
            "cpi": round(cpi_avg, 4),
            "cpd_means": cpd_means,
            "user_cpis": [u['cpi'] for u in users],
            "respondents": len(users),
        }

    return details


def run_unified():
    """Run the full unified SRI pipeline."""
    print("=" * 60)
    print("  SRI Unified Pipeline — All 5 Constructs + SET")
    print("=" * 60)

    # ── C1 ──
    print("\n[C1] Intent Readiness (max 20)...")
    c1 = compute_c1_detail()
    print(f"  {len(c1)} branches")

    # ── C2 ──
    print("[C2] Practice Readiness (max 25)...")
    c2 = compute_c2_detail()
    print(f"  {len(c2)} branches")

    # ── C3 ──
    print("[C3] Capacity Readiness (max 20)...")
    c3 = compute_c3_detail()
    print(f"  {len(c3)} branches")

    # ── C4 (summary scores) ──
    print("[C4] System Readiness (max 20)...")
    c4_scores = compute_c4()
    print(f"  {len(c4_scores)} branches")

    # ── C4 detail: area means from baseline ──
    print("  Loading baseline area detail...")
    _, area_data = load_baseline_data()

    # ── SRI Audit ──
    print("  Loading SRI audit data...")
    sri_file = os.path.join(BASE, 'data', 'extracted', 'constructs', 'sri_audit.jsonl')
    sri_by_branch = load_sri_audit_data(sri_file)
    sri_audit_scores = {}
    for bc, attempts in sri_by_branch.items():
        result = score_sri_audit(attempts)
        if result:
            sri_audit_scores[bc] = result
    print(f"  SRI audit: {len(sri_audit_scores)} branches")

    # ── SET ──
    print("[SET] Structured Explanation of Translation...")
    orientation = load_orientation_data()
    depth_data_set, _ = load_baseline_data()

    set_results = {}
    for bc in orientation:
        if bc in DEV_BRANCHES or not bc:
            continue
        ori = orientation[bc]
        if not ori["teacher_fps"] and not ori["leader_fps"]:
            continue
        depths = depth_data_set.get(bc, {})
        areas = area_data.get(bc, {
            "teacher": {a: {s: [] for s in TEACHER_AREAS[a]["subareas"]} for a in TEACHER_AREAS},
            "leader": {b: {s: [] for s in LEADER_AREAS[b]["subareas"]} for b in LEADER_AREAS},
        })
        set1 = compute_set1(ori["leader_fps"], ori["teacher_fps"], depths)
        set2_t = compute_set2_teacher(areas["teacher"])
        set2_l = compute_set2_leader(areas["leader"])
        explainers = generate_fp_explainers(set1, set2_t, set2_l)
        archetypes = detect_archetypes(set1, set2_t, set2_l)
        set_results[bc] = {
            "set1": set1, "set2_teacher": set2_t, "set2_leader": set2_l,
            "explainers": explainers, "archetypes": archetypes,
        }
    print(f"  SET: {len(set_results)} branches")

    # ── C5 placeholder ──
    print("[C5] Ecosystem Readiness (max 15) — no data")

    # ── Merge ──
    print("\n[MERGE] Building unified JSON...")
    code_to_name = build_code_to_name()
    all_bc = sorted((set(c1) | set(c2) | set(c3) | set(c4_scores) | set(set_results)) - EXCLUDED_BRANCH_CODES - DEV_BRANCHES)

    branches = {}
    for bc in all_bc:
        if not bc:
            continue
        name_tuple = code_to_name.get(bc, ("", ""))
        branch_name = name_tuple[0] if isinstance(name_tuple, tuple) else name_tuple.get("branchName", "")
        school_name = name_tuple[1] if isinstance(name_tuple, tuple) else name_tuple.get("schoolName", "")
        c1d = c1.get(bc, {})
        c2d = c2.get(bc, {})
        c3d = c3.get(bc, {})
        c4s = c4_scores.get(bc, {})

        # C4 detail from area_data
        ad = area_data.get(bc, {})
        c4_area_means_t = {}
        c4_area_bands_t = {}
        c4_subarea_means_t = {}
        for area_code in TEACHER_AREAS:
            raw = ad.get("teacher", {}).get(area_code, {})
            all_vals = []
            for sub in TEACHER_AREAS[area_code]["subareas"]:
                vals = raw.get(sub, [])
                key = f"{area_code}_{sub}"
                if vals:
                    m = sum(vals) / len(vals)
                    c4_subarea_means_t[key] = round(m, 2)
                    all_vals.extend(vals)
                else:
                    c4_subarea_means_t[key] = 0
            if all_vals:
                am = sum(all_vals) / len(all_vals)
                c4_area_means_t[area_code] = round(am, 2)
                c4_area_bands_t[area_code] = "high" if am > 3.2 else ("mid" if am >= 2.5 else "low")
            else:
                c4_area_means_t[area_code] = 0
                c4_area_bands_t[area_code] = "low"

        c4_area_means_l = {}
        c4_area_bands_l = {}
        c4_subarea_means_l = {}
        for area_code in LEADER_AREAS:
            raw = ad.get("leader", {}).get(area_code, {})
            all_vals = []
            for sub in LEADER_AREAS[area_code]["subareas"]:
                vals = raw.get(sub, [])
                key = f"{area_code}_{sub}"
                if vals:
                    m = sum(vals) / len(vals)
                    c4_subarea_means_l[key] = round(m, 2)
                    all_vals.extend(vals)
                else:
                    c4_subarea_means_l[key] = 0
            if all_vals:
                am = sum(all_vals) / len(all_vals)
                c4_area_means_l[area_code] = round(am, 2)
                c4_area_bands_l[area_code] = "high" if am > 3.2 else ("mid" if am >= 2.5 else "low")
            else:
                c4_area_means_l[area_code] = 0
                c4_area_bands_l[area_code] = "low"

        # SRI audit
        audit = sri_audit_scores.get(bc)
        audit_data = None
        if audit:
            audit_data = {
                "system_readiness": audit["system_readiness"],
                "band": audit["band"],
                "teacher_enablement": audit["teacher_enablement"],
                "leadership_routines": audit["leadership_routines"],
                "enablement_items": audit["enablement_items"],
                "routine_items": audit["routine_items"],
                "respondent_count": audit["respondent_count"],
            }

        # SET
        set_data = _serialize(set_results.get(bc))

        # Summary scores
        s_c1 = c1d.get("C1", 0)
        s_c2 = c2d.get("C2", 0)
        s_c3 = c3d.get("C3", 0)
        s_c4 = c4s.get("C4", 0)
        s_c5 = 0
        sri_total = s_c1 + s_c2 + s_c3 + s_c4 + s_c5

        branches[bc] = {
            "branchName": branch_name,
            "schoolName": school_name,
            "summary": {
                "C1": s_c1, "C2": s_c2, "C3": s_c3, "C4": s_c4, "C5": s_c5,
                "SRI_Total": round(sri_total, 2),
                "SRI_Pct": round(sri_total / 100 * 100, 1),
            },
            "c1_detail": c1d if c1d else None,
            "c2_detail": c2d if c2d else None,
            "c3_detail": c3d if c3d else None,
            "c4_detail": {
                "C4": s_c4,
                "enablement": c4s.get("C4_Enablement", 0),
                "routine": c4s.get("C4_Routine", 0),
                "area_means_teacher": c4_area_means_t,
                "area_bands_teacher": c4_area_bands_t,
                "subarea_means_teacher": c4_subarea_means_t,
                "area_means_leader": c4_area_means_l,
                "area_bands_leader": c4_area_bands_l,
                "subarea_means_leader": c4_subarea_means_l,
            },
            "c5_detail": None,
            "sri_audit": audit_data,
            "set": set_data,
        }

    # ── Write ──
    os.makedirs(REPORTS, exist_ok=True)
    unified = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "total_branches": len(branches),
            "sri_max": 100,
            "construct_weights": {"C1": 20, "C2": 25, "C3": 20, "C4": 20, "C5": 15},
        },
        "branches": branches,
    }

    json_path = os.path.join(REPORTS, 'sri_unified.json')
    with open(json_path, 'w') as f:
        json.dump(unified, f, indent=2, default=str)
    print(f"\n  Written: {json_path} ({os.path.getsize(json_path) / 1024:.0f} KB)")
    print(f"  Branches: {len(branches)}")

    # Quick stats
    totals = [b["summary"]["SRI_Total"] for b in branches.values() if b["summary"]["SRI_Total"] > 0]
    if totals:
        print(f"  SRI range: {min(totals):.1f} – {max(totals):.1f} (avg {sum(totals)/len(totals):.1f})")

    return unified


def _serialize(obj):
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    if callable(obj):
        return str(obj)
    return obj


if __name__ == "__main__":
    run_unified()
