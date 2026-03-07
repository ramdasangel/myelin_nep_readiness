#!/usr/bin/env python3
"""Parse all-constructs extraction into structured CSVs."""
import json
import csv
import os

RAW_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'myelin_stat_ro', 'all_constructs_raw.txt')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'myelin_stat_ro')

with open(RAW_FILE, 'r') as f:
    content = f.read()

def extract_json(content, start_marker, end_marker):
    s = content.index(start_marker) + len(start_marker)
    e = content.index(end_marker)
    return json.loads(content[s:e].strip())

# ============================
# 1. All Question Sets inventory
# ============================
all_sets = extract_json(content, 'JSON_START_ALLSETS\n', '\nJSON_END_ALLSETS')
out = os.path.join(OUT_DIR, 'all_question_sets.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['setCode', 'setName', 'questionCount'])
    for s in all_sets:
        w.writerow([s['setCode'], s['setName'], s['questionCount']])
print(f"Wrote {len(all_sets)} question sets to {out}")

# ============================
# 2. Baseline Questions (System Readiness)
# ============================
baseline_questions = extract_json(content, 'JSON_START_BASELINE_Q\n', '\nJSON_END_BASELINE_Q')
q_lookup = {q['questionId']: q for q in baseline_questions}

out = os.path.join(OUT_DIR, 'system_readiness_questions.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['questionId', 'questionText', 'goal', 'description',
                'opt0_text', 'opt1_text', 'opt2_text', 'opt3_text'])
    for q in baseline_questions:
        opts = q.get('options', [])
        row = [q['questionId'], q['questionText'], q['goal'], q.get('description', '')]
        for i in range(4):
            row.append(opts[i]['text'] if i < len(opts) else '')
        w.writerow(row)
print(f"Wrote {len(baseline_questions)} baseline questions to {out}")

# ============================
# 3. Baseline Attempts (System Readiness)
# ============================
baseline_attempts = extract_json(content, 'JSON_START_BASELINE_A\n', '\nJSON_END_BASELINE_A')

# Flat attempts CSV
max_q = max(a['responseCount'] for a in baseline_attempts) if baseline_attempts else 0
out = os.path.join(OUT_DIR, 'system_readiness_attempts.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    header = ['attemptId', 'userId', 'firstName', 'lastName', 'role',
              'branchId', 'branchName', 'schoolName', 'branchCode',
              'setCode', 'submittedAt', 'responseCount']
    for i in range(max_q):
        header.extend([f'q{i+1}_id', f'q{i+1}_goal', f'q{i+1}_selectedOption'])
    w.writerow(header)
    for a in baseline_attempts:
        row = [a['attemptId'], a['userId'], a['firstName'], a['lastName'],
               a['role'], a['branchId'], a['branchName'], a['schoolName'],
               a['branchCode'], a['setCode'], a.get('submittedAt', ''), a['responseCount']]
        for r in a.get('responses', []):
            qid = r.get('questionId', '')
            q = q_lookup.get(qid, {})
            row.extend([qid, q.get('goal', ''), r.get('selectedOption', '')])
        for _ in range(len(a.get('responses', [])), max_q):
            row.extend(['', '', ''])
        w.writerow(row)
print(f"Wrote {len(baseline_attempts)} baseline attempts to {out}")

# Detailed responses CSV
out = os.path.join(OUT_DIR, 'system_readiness_responses_detail.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['userId', 'firstName', 'lastName', 'role', 'branchCode', 'branchName',
                'schoolName', 'setCode', 'attemptId', 'questionId', 'questionText',
                'goal', 'selectedOption', 'selectedOptionText'])
    count = 0
    for a in baseline_attempts:
        for r in a.get('responses', []):
            qid = r.get('questionId', '')
            q = q_lookup.get(qid, {})
            sel = r.get('selectedOption')
            opts = q.get('options', [])
            sel_text = ''
            try:
                sel_int = int(sel) if sel is not None else -1
            except (ValueError, TypeError):
                sel_int = -1
            if sel_int >= 0 and sel_int < len(opts):
                sel_text = opts[sel_int]['text']
            w.writerow([
                a['userId'], a['firstName'], a['lastName'], a['role'],
                a['branchCode'], a['branchName'], a['schoolName'],
                a['setCode'], a['attemptId'], qid,
                q.get('questionText', ''), q.get('goal', ''),
                sel, sel_text
            ])
            count += 1
print(f"Wrote {count} baseline response rows to {out}")

# ============================
# Summary
# ============================
print("\n=== SYSTEM READINESS BREAKDOWN ===")
by_code = {}
by_role = {}
by_branch = {}
for a in baseline_attempts:
    code = a['setCode']
    role = a['role']
    branch = f"{a['branchCode']}|{a['branchName']}"
    by_code[code] = by_code.get(code, 0) + 1
    by_role[role] = by_role.get(role, 0) + 1
    by_branch[branch] = by_branch.get(branch, 0) + 1

print("\nBy setCode:")
for k, v in sorted(by_code.items()):
    print(f"  {k}: {v}")
print(f"\nBy role:")
for k, v in sorted(by_role.items()):
    print(f"  {k}: {v}")
print(f"\nUnique branches: {len(by_branch)}")
