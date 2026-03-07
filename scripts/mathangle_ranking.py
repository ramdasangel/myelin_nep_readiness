#!/usr/bin/env python3
"""Mathangle Assessment — Teacher/Leader competency ranking report."""

import json
import csv
import sys
from collections import defaultdict

INPUT = "/tmp/mathangle_raw.jsonl"
OUT_DIR = "/Users/ramdasangel/MyelinMaster/myelin_nep_readiness/output"

# English ↔ Marathi chapter mapping (unified competency areas)
CHAPTER_MAP = {
    # Arithmetic
    "Addition": "Addition & Subtraction",
    "बेरीज": "Addition & Subtraction",
    "Multiplication": "Multiplication",
    "गुणाकार": "Multiplication",
    "Division": "Division",
    "भागाकार": "Division",
    # Number Theory
    "Factors & Multiples": "Factors & Multiples",
    "विभाज्य आणि विभाजक": "Factors & Multiples",
    # Geometry
    "Geometry": "Geometry",
    "भूमिती": "Geometry",
    # Measurement
    "Measurement": "Measurement",
    "मापन": "Measurement",
    # Money
    "Money": "Money",
    "पैसे": "Money",
    # Time & Calendar
    "Time & Calendar": "Time & Calendar",
    "वेळ आणि दिनदर्शिका": "Time & Calendar",
}


def map_chapter(chapter_name):
    """Map a chapter name to a unified competency area."""
    for key, area in CHAPTER_MAP.items():
        if chapter_name.startswith(key):
            return area
    return chapter_name  # fallback


def load_data():
    rows = []
    with open(INPUT) as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            rows.append(json.loads(line))
    return rows


def build_ranking(rows):
    """Build per-person competency summary."""
    people = []
    for r in rows:
        # Aggregate chapter-wise into unified competency areas
        area_scores = defaultdict(lambda: {"right": 0, "total": 0})
        for ch in r.get("chapterWise", []):
            area = map_chapter(ch["chapter"])
            area_scores[area]["right"] += ch["right"]
            area_scores[area]["total"] += ch["total"]

        # Cognitive levels
        cog = {}
        for c in r.get("cognitiveLevel", []):
            cog[c["level"]] = {"right": c["right"], "total": c["total"], "pct": c["pct"]}

        # Difficulty levels
        diff = {}
        for q in r.get("questionLevel", []):
            diff[q["level"]] = {"right": q["right"], "total": q["total"]}

        person = {
            "name": f'{r["firstName"]} {r["lastName"]}'.strip(),
            "role": r["role"],
            "branch": r["branchName"],
            "school": r["schoolName"],
            "language": "MR" if "मराठी" in r["testName"] else "EN",
            "totalObtained": r["totalObtained"],
            "totalMarks": r["totalMarks"],
            "percentage": r["percentage"],
            "timeTaken": r["timeTaken"],
            "areas": dict(area_scores),
            "cognitive": cog,
            "difficulty": diff,
            "runDate": r.get("runDate", ""),
        }
        people.append(person)

    # Sort by percentage descending
    people.sort(key=lambda x: x["percentage"], reverse=True)
    return people


def write_overall_csv(people):
    """Write overall ranking CSV."""
    all_areas = sorted(
        {a for p in people for a in p["areas"]},
        key=lambda x: x,
    )
    cog_levels = ["Understand", "Apply", "Analyze", "Evaluate"]
    diff_levels = [1, 2, 3]

    path = f"{OUT_DIR}/mathangle_ranking.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        # Header
        header = [
            "Rank", "Name", "Role", "Branch", "School", "Language",
            "Score", "Total", "Percentage", "Time Taken",
        ]
        for a in all_areas:
            header.append(f"{a} (%)")
        for c in cog_levels:
            header.append(f"Cog: {c} (%)")
        for d in diff_levels:
            header.append(f"Level {d} (R/T)")
        w.writerow(header)

        for rank, p in enumerate(people, 1):
            row = [
                rank, p["name"], p["role"], p["branch"], p["school"], p["language"],
                p["totalObtained"], p["totalMarks"], p["percentage"], p["timeTaken"],
            ]
            for a in all_areas:
                if a in p["areas"]:
                    s = p["areas"][a]
                    pct = round(s["right"] / s["total"] * 100, 1) if s["total"] > 0 else 0
                    row.append(pct)
                else:
                    row.append("")
            for c in cog_levels:
                if c in p["cognitive"]:
                    row.append(p["cognitive"][c]["pct"])
                else:
                    row.append("")
            for d in diff_levels:
                if d in p["difficulty"]:
                    row.append(f'{p["difficulty"][d]["right"]}/{p["difficulty"][d]["total"]}')
                else:
                    row.append("")
            w.writerow(row)

    print(f"Wrote {path} — {len(people)} rows")
    return path


def print_summary(people):
    """Print summary stats to stdout."""
    teachers = [p for p in people if p["role"] == "Teacher"]
    leaders = [p for p in people if p["role"] == "Leader"]

    print(f"\n{'='*70}")
    print(f"MATHANGLE ASSESSMENT SUMMARY")
    print(f"{'='*70}")
    print(f"Total responses: {len(people)}  (Teachers: {len(teachers)}, Leaders: {len(leaders)})")

    for label, group in [("ALL", people), ("Teachers", teachers), ("Leaders", leaders)]:
        if not group:
            continue
        pcts = [p["percentage"] for p in group]
        print(f"\n--- {label} ({len(group)}) ---")
        print(f"  Avg: {sum(pcts)/len(pcts):.1f}%  |  Max: {max(pcts):.1f}%  |  Min: {min(pcts):.1f}%")

        # Competency area averages
        area_totals = defaultdict(lambda: {"right": 0, "total": 0})
        for p in group:
            for a, s in p["areas"].items():
                area_totals[a]["right"] += s["right"]
                area_totals[a]["total"] += s["total"]
        print(f"  Competency Areas:")
        for a in sorted(area_totals.keys()):
            s = area_totals[a]
            pct = round(s["right"] / s["total"] * 100, 1) if s["total"] > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"    {a:25s} {bar} {pct:5.1f}%  ({s['right']}/{s['total']})")

        # Cognitive level averages
        cog_totals = defaultdict(lambda: {"right": 0, "total": 0})
        for p in group:
            for c, s in p["cognitive"].items():
                cog_totals[c]["right"] += s["right"]
                cog_totals[c]["total"] += s["total"]
        print(f"  Cognitive Levels (Bloom's):")
        for c in ["Understand", "Apply", "Analyze", "Evaluate"]:
            if c in cog_totals:
                s = cog_totals[c]
                pct = round(s["right"] / s["total"] * 100, 1) if s["total"] > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"    {c:25s} {bar} {pct:5.1f}%  ({s['right']}/{s['total']})")

    # Top 10 & Bottom 10
    print(f"\n{'='*70}")
    print("TOP 10 PERFORMERS")
    print(f"{'='*70}")
    print(f"{'Rank':>4}  {'Name':30s} {'Role':8s} {'Branch':35s} {'Score':>6} {'%':>7}")
    for i, p in enumerate(people[:10], 1):
        print(f"{i:4d}  {p['name']:30s} {p['role']:8s} {p['branch']:35s} {p['totalObtained']:>3}/{p['totalMarks']:<3} {p['percentage']:6.1f}%")

    print(f"\n{'='*70}")
    print("BOTTOM 10 PERFORMERS")
    print(f"{'='*70}")
    print(f"{'Rank':>4}  {'Name':30s} {'Role':8s} {'Branch':35s} {'Score':>6} {'%':>7}")
    for i, p in enumerate(people[-10:], len(people) - 9):
        print(f"{i:4d}  {p['name']:30s} {p['role']:8s} {p['branch']:35s} {p['totalObtained']:>3}/{p['totalMarks']:<3} {p['percentage']:6.1f}%")


if __name__ == "__main__":
    rows = load_data()
    print(f"Loaded {len(rows)} Mathangle results")
    people = build_ranking(rows)
    write_overall_csv(people)
    print_summary(people)
