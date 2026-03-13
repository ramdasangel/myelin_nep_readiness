#!/usr/bin/env python3
"""Dump all Mathangle data into comprehensive CSV files."""

import json
import csv
from collections import defaultdict
from pathlib import Path

RAW = "/tmp/mathangle_raw.jsonl"
EXIT = "/tmp/mathangle_exit_levels.jsonl"
INDECISION = "/tmp/mathangle_indecision.jsonl"
OUT = Path("/Users/ramdasangel/MyelinMaster/myelin_nep_readiness/output")

CHAPTER_MAP = {
    "Addition": "Addition & Subtraction", "बेरीज": "Addition & Subtraction",
    "Multiplication": "Multiplication", "गुणाकार": "Multiplication",
    "Division": "Division", "भागाकार": "Division",
    "Factors & Multiples": "Factors & Multiples", "विभाज्य आणि विभाजक": "Factors & Multiples",
    "Geometry": "Geometry", "भूमिती": "Geometry",
    "Measurement": "Measurement", "मापन": "Measurement",
    "Money": "Money", "पैसे": "Money",
    "Time & Calendar": "Time & Calendar", "वेळ आणि दिनदर्शिका": "Time & Calendar",
}
SUBTOPIC_MAP = {
    "Multiplication": "Multiplication",
    "Currency, openarions on money": "Money",
    "LCM": "Factors & Multiples", "LCM, Time measurement": "Factors & Multiples",
    "Divisibility Tests": "Factors & Multiples",
    "Division": "Division",
    "Length measurement": "Measurement", "Length measurement, conversion": "Measurement",
    "Addition, Subtraction": "Addition & Subtraction",
    "Minutes, Hours, Seconds measurement": "Time & Calendar",
    "Types of angles and shapes": "Geometry", "Measuring angles": "Geometry",
}
EXIT_LABELS = {1: "Foundational", 2: "Preparatory", 3: "Middle"}
AREAS = ["Multiplication", "Money", "Factors & Multiples", "Division",
         "Measurement", "Addition & Subtraction", "Time & Calendar", "Geometry"]
COGS = ["Understand", "Apply", "Analyze", "Evaluate"]

# Exclude test/demo branches and test users
EXCLUDED_BRANCHES = {"DES Demo", "Myelin Cbse Primary & Secondary School"}

def _is_excluded(row):
    if row.get("branchName", row.get("branch", "")) in EXCLUDED_BRANCHES:
        return True
    ln = row.get("lastName", "")
    if not ln:
        name = row.get("name", "")
        ln = name.split()[-1] if name.split() else ""
    if ln and ln.strip().lower() == "test":
        return True
    return False

def mc(ch):
    for k, v in CHAPTER_MAP.items():
        if ch.startswith(k): return v
    return ch

def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"): rows.append(json.loads(line))
    return rows

def compute_exit(exit_rows):
    result = {}
    for er in exit_rows:
        sid = er["studentId"]
        comp_levels = defaultdict(dict)
        for subtopic, levels in er.get("topicLevels", {}).items():
            comp = SUBTOPIC_MAP.get(subtopic)
            if not comp: continue
            for lv_str, data in levels.items():
                lv = int(lv_str)
                if lv not in comp_levels[comp] or data["right"] > comp_levels[comp][lv]:
                    comp_levels[comp][lv] = data["right"]
        exit_map = {}
        for comp in AREAS:
            if comp not in comp_levels:
                exit_map[comp] = "Not Assessed"
                continue
            levels = comp_levels[comp]
            highest = None
            for lv in sorted(levels.keys(), reverse=True):
                if levels[lv] > 0:
                    highest = lv; break
            exit_map[comp] = EXIT_LABELS[highest] if highest else "Below Foundational"
        result[sid] = exit_map
    return result

def compute_indecision(ind_rows):
    result = {}
    for ir in ind_rows:
        sid = ir["studentId"]
        tq = ir["totalQs"] or 1
        tc = ir["totalChanges"]
        tff = ir["totalFlipFlops"]
        tt = max(ir["totalTime"], 1)
        ct = ir["changeTime"]
        cfc = sum(1 for pq in ir["perQuestion"] if pq.get("changedFromCorrect"))
        ctc = sum(1 for pq in ir["perQuestion"] if pq.get("changedToCorrect"))
        cpq = tc / tq
        score = (
            min(cpq / 4, 1.0) * 40 +
            (tff / tq) * 25 +
            min(ct / tt, 1.0) * 15 +
            (cfc / tq) * 20
        )
        result[sid] = {
            "score": round(min(score, 100), 1),
            "totalChanges": tc, "flipFlops": tff,
            "changesPerQ": round(cpq, 2),
            "changeTime": ct,
            "fromCorrect": cfc, "toCorrect": ctc,
            "perQuestion": ir["perQuestion"],
        }
    return result

def main():
    raw = [r for r in load_jsonl(RAW) if not _is_excluded(r)]
    exit_rows = [r for r in load_jsonl(EXIT) if not _is_excluded(r)]
    ind_rows = [r for r in load_jsonl(INDECISION) if not _is_excluded(r)]
    exits = compute_exit(exit_rows)
    inds = compute_indecision(ind_rows)

    # ── CSV 1: Master ranking with all data ──────────────────────────
    path1 = OUT / "mathangle_master.csv"
    with open(path1, "w", newline="") as f:
        w = csv.writer(f)
        header = [
            "Rank", "StudentId", "Name", "Role", "Branch", "School", "Language",
            "Score", "TotalMarks", "Percentage", "TimeTaken",
        ]
        for a in AREAS: header.append(f"{a} (%)")
        for a in AREAS: header.append(f"{a} (Right)")
        for a in AREAS: header.append(f"{a} (Total)")
        for c in COGS: header.append(f"Cog:{c} (%)")
        for c in COGS: header.append(f"Cog:{c} (Right)")
        for c in COGS: header.append(f"Cog:{c} (Total)")
        header += ["Diff:L1 (Right)", "Diff:L1 (Total)", "Diff:L2 (Right)", "Diff:L2 (Total)",
                    "Diff:L3 (Right)", "Diff:L3 (Total)"]
        for a in AREAS: header.append(f"Exit:{a}")
        header += [
            "Indecision Score", "Total Changes", "Changes/Q", "Flip-Flops",
            "Changed→Wrong", "Changed→Right", "Net Harm", "Change Time (s)"
        ]
        w.writerow(header)

        sorted_raw = sorted(raw, key=lambda x: x["percentage"], reverse=True)
        for rank, r in enumerate(sorted_raw, 1):
            sid = r["studentId"]
            name = f'{r["firstName"]} {r["lastName"]}'.strip()
            lang = "MR" if "मराठी" in r["testName"] else "EN"

            # Area scores
            areas_raw = defaultdict(lambda: {"right": 0, "total": 0})
            for ch in r.get("chapterWise", []):
                a = mc(ch["chapter"])
                areas_raw[a]["right"] += ch["right"]
                areas_raw[a]["total"] += ch["total"]

            # Cog scores
            cog_data = {}
            for c in r.get("cognitiveLevel", []):
                cog_data[c["level"]] = c

            # Diff scores
            diff_data = {}
            for q in r.get("questionLevel", []):
                diff_data[q["level"]] = q

            # Exit
            el = exits.get(sid, {})
            # Indecision
            ind = inds.get(sid, {})

            row = [
                rank, sid, name, r["role"], r["branchName"], r["schoolName"], lang,
                r["totalObtained"], r["totalMarks"], r["percentage"], r["timeTaken"],
            ]
            # Area %
            for a in AREAS:
                s = areas_raw.get(a, {"right": 0, "total": 0})
                row.append(round(s["right"]/s["total"]*100, 1) if s["total"] else "")
            # Area right
            for a in AREAS:
                s = areas_raw.get(a, {"right": 0, "total": 0})
                row.append(s["right"] if s["total"] else "")
            # Area total
            for a in AREAS:
                s = areas_raw.get(a, {"right": 0, "total": 0})
                row.append(s["total"] if s["total"] else "")
            # Cog %
            for c in COGS:
                cd = cog_data.get(c, {})
                row.append(cd.get("pct", ""))
            # Cog right
            for c in COGS:
                cd = cog_data.get(c, {})
                row.append(cd.get("right", ""))
            # Cog total
            for c in COGS:
                cd = cog_data.get(c, {})
                row.append(cd.get("total", ""))
            # Diff
            for d in [1, 2, 3]:
                dd = diff_data.get(d, {})
                row.append(dd.get("right", ""))
                row.append(dd.get("total", ""))
            # Exit levels
            for a in AREAS:
                row.append(el.get(a, ""))
            # Indecision
            row.append(ind.get("score", 0))
            row.append(ind.get("totalChanges", 0))
            row.append(ind.get("changesPerQ", 0))
            row.append(ind.get("flipFlops", 0))
            row.append(ind.get("fromCorrect", 0))
            row.append(ind.get("toCorrect", 0))
            row.append(ind.get("fromCorrect", 0) - ind.get("toCorrect", 0))
            row.append(ind.get("changeTime", 0))

            w.writerow(row)

    print(f"1. {path1} — {rank} rows, {len(header)} columns")

    # ── CSV 2: Per-question responses with indecision detail ─────────
    path2 = OUT / "mathangle_per_question.csv"
    with open(path2, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "StudentId", "Name", "Role", "Branch", "Language",
            "QuestionId", "Subtopic", "CompetencyArea", "QuestionLevel",
            "Correct", "TimeTaken(s)",
            "SeqLength", "NumChanges", "FlipFlop",
            "DeliberationTime(s)", "FirstChoice", "FinalChoice", "CorrectAnswer",
            "ChangedFromCorrect", "ChangedToCorrect",
        ])
        for ir in ind_rows:
            sid = ir["studentId"]
            for pq in ir["perQuestion"]:
                comp = SUBTOPIC_MAP.get(pq["subtopic"], pq["subtopic"])
                w.writerow([
                    sid, ir["name"], ir["role"], ir["branch"], ir["lang"],
                    pq["qId"], pq["subtopic"], comp, pq["qLevel"],
                    pq["correct"], pq["timeTaken"],
                    pq["seqLen"], pq["numChanges"], pq["flipFlop"],
                    pq["deliberationTime"], pq.get("firstChoice", ""), pq.get("finalChoice", ""),
                    pq.get("correctAnswer", ""),
                    pq.get("changedFromCorrect", 0), pq.get("changedToCorrect", 0),
                ])
    qcount = sum(len(ir["perQuestion"]) for ir in ind_rows)
    print(f"2. {path2} — {qcount} question-response rows")

    # ── CSV 3: Branch summary ────────────────────────────────────────
    path3 = OUT / "mathangle_branch_summary.csv"
    branch_map = defaultdict(list)
    for r in raw:
        branch_map[r["branchName"]].append(r)

    with open(path3, "w", newline="") as f:
        w = csv.writer(f)
        header = ["Branch", "School", "Respondents", "Teachers", "Leaders", "AvgScore(%)"]
        for a in AREAS: header.append(f"{a} (%)")
        w.writerow(header)
        for br in sorted(branch_map, key=lambda b: sum(r["percentage"] for r in branch_map[b])/len(branch_map[b]), reverse=True):
            br_rows = branch_map[br]
            avg = round(sum(r["percentage"] for r in br_rows) / len(br_rows), 1)
            school = br_rows[0]["schoolName"]
            teachers = sum(1 for r in br_rows if r["role"] == "Teacher")
            leaders = sum(1 for r in br_rows if r["role"] == "Leader")
            row = [br, school, len(br_rows), teachers, leaders, avg]
            for a in AREAS:
                right = sum(r_raw for r in br_rows for ch in r.get("chapterWise", [])
                           if mc(ch["chapter"]) == a for r_raw in [ch["right"]])
                total = sum(t_raw for r in br_rows for ch in r.get("chapterWise", [])
                           if mc(ch["chapter"]) == a for t_raw in [ch["total"]])
                row.append(round(right/total*100, 1) if total else "")
            w.writerow(row)
    print(f"3. {path3} — {len(branch_map)} branches")

    # ── CSV 4: Exit level matrix ─────────────────────────────────────
    path4 = OUT / "mathangle_exit_levels.csv"
    with open(path4, "w", newline="") as f:
        w = csv.writer(f)
        header = ["StudentId", "Name", "Role", "Branch", "Language", "Percentage"]
        for a in AREAS: header.append(f"Exit:{a}")
        w.writerow(header)
        for r in sorted(raw, key=lambda x: x["percentage"], reverse=True):
            sid = r["studentId"]
            el = exits.get(sid, {})
            name = f'{r["firstName"]} {r["lastName"]}'.strip()
            lang = "MR" if "मराठी" in r["testName"] else "EN"
            row = [sid, name, r["role"], r["branchName"], lang, r["percentage"]]
            for a in AREAS: row.append(el.get(a, ""))
            w.writerow(row)
    print(f"4. {path4} — {len(raw)} rows")

    print(f"\nAll CSVs written to {OUT}/")

if __name__ == "__main__":
    main()
