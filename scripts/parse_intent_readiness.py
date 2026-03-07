#!/usr/bin/env python3
"""Parse raw Intent Readiness extraction into structured CSVs."""
import json
import csv
import os

RAW_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'myelin_stat_ro', 'intent_readiness_raw.txt')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'myelin_stat_ro')

# Read raw file
with open(RAW_FILE, 'r') as f:
    content = f.read()

# Parse questions JSON
q_start = content.index('JSON_START_QUESTIONS') + len('JSON_START_QUESTIONS\n')
q_end = content.index('JSON_END_QUESTIONS')
questions = json.loads(content[q_start:q_end].strip())

# Parse attempts JSON
a_start = content.index('JSON_START_ATTEMPTS') + len('JSON_START_ATTEMPTS\n')
a_end = content.index('JSON_END_ATTEMPTS')
attempts = json.loads(content[a_start:a_end].strip())

# Build question lookup
q_lookup = {q['questionId']: q for q in questions}

# --- Output 1: Questions CSV ---
q_out = os.path.join(OUT_DIR, 'intent_questions.csv')
with open(q_out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['questionId', 'questionText', 'goal', 'description',
                'opt0_text', 'opt0_fp', 'opt1_text', 'opt1_fp',
                'opt2_text', 'opt2_fp', 'opt3_text', 'opt3_fp'])
    for q in questions:
        opts = q.get('options', [])
        row = [q['questionId'], q['questionText'], q['goal'], q.get('description', '')]
        for i in range(4):
            if i < len(opts):
                row.extend([opts[i]['text'], opts[i].get('fp', '')])
            else:
                row.extend(['', ''])
        w.writerow(row)
print(f"Wrote {len(questions)} questions to {q_out}")

# --- Output 2: Attempts flat CSV (one row per attempt, responses as columns) ---
# First, figure out max questions per attempt
max_q = max(a['responseCount'] for a in attempts) if attempts else 0
print(f"Max questions per attempt: {max_q}")

a_out = os.path.join(OUT_DIR, 'intent_attempts.csv')
with open(a_out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    header = ['attemptId', 'userId', 'firstName', 'lastName', 'role', 'mobile',
              'branchId', 'branchName', 'schoolName', 'branchCode',
              'setCode', 'submittedAt', 'responseCount']
    # Add response columns
    for i in range(max_q):
        header.extend([f'q{i+1}_id', f'q{i+1}_text', f'q{i+1}_goal', f'q{i+1}_selectedOption'])
    w.writerow(header)

    for a in attempts:
        row = [a['attemptId'], a['userId'], a['firstName'], a['lastName'],
               a['role'], a['mobile'], a['branchId'], a['branchName'],
               a['schoolName'], a['branchCode'], a['setCode'],
               a.get('submittedAt', ''), a['responseCount']]
        for i, r in enumerate(a.get('responses', [])):
            qid = r.get('questionId', '')
            q = q_lookup.get(qid, {})
            row.extend([qid, q.get('questionText', '')[:80], q.get('goal', ''), r.get('selectedOption', '')])
        # Pad if fewer responses
        for i in range(len(a.get('responses', [])), max_q):
            row.extend(['', '', '', ''])
        w.writerow(row)
print(f"Wrote {len(attempts)} attempts to {a_out}")

# --- Output 3: Responses detail CSV (one row per question-response) ---
r_out = os.path.join(OUT_DIR, 'intent_responses_detail.csv')
with open(r_out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['userId', 'firstName', 'lastName', 'role', 'branchCode', 'branchName',
                'schoolName', 'setCode', 'attemptId', 'questionId', 'questionText',
                'goal', 'selectedOption', 'selectedOptionText'])
    count = 0
    for a in attempts:
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
print(f"Wrote {count} response rows to {r_out}")

# --- Summary stats ---
print("\n=== SUMMARY ===")
by_code = {}
by_role = {}
by_branch = {}
for a in attempts:
    code = a['setCode']
    role = a['role']
    branch = f"{a['branchCode']}|{a['branchName']}"
    by_code[code] = by_code.get(code, 0) + 1
    by_role[role] = by_role.get(role, 0) + 1
    by_branch[branch] = by_branch.get(branch, 0) + 1

print("\nBy setCode:")
for k, v in sorted(by_code.items()):
    print(f"  {k}: {v}")

print("\nBy role:")
for k, v in sorted(by_role.items()):
    print(f"  {k}: {v}")

print(f"\nUnique branches: {len(by_branch)}")
print("\nBy branch:")
for k, v in sorted(by_branch.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
