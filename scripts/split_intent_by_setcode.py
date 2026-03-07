#!/usr/bin/env python3
"""Split intent questions, attempts, and responses into 4 files by setCode."""
import csv
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'myelin_stat_ro')

SET_LABELS = {
    '1234': 'intent_teacher_english',
    '103':  'intent_teacher_marathi',
    '7890': 'intent_leader_english',
    '104':  'intent_leader_marathi',
}

# 1. Split questions
print("=== Splitting intent_questions.csv ===")
with open(os.path.join(BASE, 'intent_questions.csv'), 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Build questionId → setCode mapping from attempts
# First, read responses to map questionId to setCode
qid_to_set = {}
with open(os.path.join(BASE, 'intent_responses_detail.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        qid = r['questionId']
        sc = r['setCode']
        if qid not in qid_to_set:
            qid_to_set[qid] = set()
        qid_to_set[qid].add(sc)

# Group questions by setCode
set_questions = {k: [] for k in SET_LABELS}
for row in rows:
    qid = row[0]
    sets = qid_to_set.get(qid, set())
    for sc in sets:
        if sc in SET_LABELS:
            set_questions[sc].append(row)

# Handle questions that appear in both en+mr of same role
# English teacher questions appear in 1234, Marathi in 103, etc.
# If a question maps to multiple setCodes, it's shared — assign to all
for sc, label in SET_LABELS.items():
    out_path = os.path.join(BASE, f'{label}_questions.csv')
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in set_questions[sc]:
            w.writerow(row)
    print(f"  {label}_questions.csv: {len(set_questions[sc])} questions")

# 2. Split attempts
print("\n=== Splitting intent_attempts.csv ===")
with open(os.path.join(BASE, 'intent_attempts.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    att_header = reader.fieldnames
    att_rows = list(reader)

set_attempts = {k: [] for k in SET_LABELS}
for row in att_rows:
    sc = row['setCode']
    if sc in SET_LABELS:
        set_attempts[sc].append(row)

for sc, label in SET_LABELS.items():
    out_path = os.path.join(BASE, f'{label}_attempts.csv')
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=att_header)
        w.writeheader()
        w.writerows(set_attempts[sc])
    print(f"  {label}_attempts.csv: {len(set_attempts[sc])} attempts")

# 3. Split responses detail
print("\n=== Splitting intent_responses_detail.csv ===")
with open(os.path.join(BASE, 'intent_responses_detail.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    resp_header = reader.fieldnames
    resp_rows = list(reader)

set_responses = {k: [] for k in SET_LABELS}
for row in resp_rows:
    sc = row['setCode']
    if sc in SET_LABELS:
        set_responses[sc].append(row)

for sc, label in SET_LABELS.items():
    out_path = os.path.join(BASE, f'{label}_responses.csv')
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=resp_header)
        w.writeheader()
        w.writerows(set_responses[sc])
    print(f"  {label}_responses.csv: {len(set_responses[sc])} responses")

print("\nDone!")
