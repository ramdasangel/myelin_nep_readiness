# Detailed FP Mapping CSV Format - Documentation

## Overview

These CSV files provide **complete transparency** into how each response maps to Foundational Philosophies (FPs), showing both the original answers and their FP classifications for every question.

---

## File Structure

### Files Generated
1. **school_leaders_detailed_fp_mapping.csv** (20 rows, 36 columns)
2. **teachers_detailed_fp_mapping.csv** (80 rows, 36 columns)

### Column Structure (36 columns total)

```
Column 1: user_id
Columns 2-31: Question Response & FP Mapping (15 questions × 2 columns each)
  - Q1_response, Q1_FP
  - Q2_response, Q2_FP
  - ... (continues through Q15)
Columns 32-36: FP Totals
  - FP1, FP2, FP3, FP4, FP5
```

---

## Column Details

### Column 1: User Identifier
- **user_id**: Unique identifier
  - Leaders: L01, L02, ..., L20
  - Teachers: T001, T002, ..., T080

### Columns 2-31: Question-by-Question Mapping
For each question (Q1 through Q15), there are **two columns**:

**Q{n}_response**: The answer selected (A, B, C, or D)
**Q{n}_FP**: Which FP that answer maps to (FP1, FP2, FP3, FP4, or FP5)

Example columns:
- Q1_response: "C"
- Q1_FP: "FP1"
- Q2_response: "A"  
- Q2_FP: "FP3"
- ... and so on

### Columns 32-36: FP Total Counts
**FP1**: Total count of FP1 selections (0-15)
**FP2**: Total count of FP2 selections (0-15)
**FP3**: Total count of FP3 selections (0-15)
**FP4**: Total count of FP4 selections (0-15)
**FP5**: Total count of FP5 selections (0-15)

Note: FP1 + FP2 + FP3 + FP4 + FP5 = 15 (total questions)

---

## Sample Data

### School Leader Example (L01)

| Column | Value | Meaning |
|--------|-------|---------|
| user_id | L01 | Leader 01 |
| Q1_response | C | Selected option C for question 1 |
| Q1_FP | FP1 | Option C maps to FP1 (Each Child is Unique) |
| Q2_response | A | Selected option A for question 2 |
| Q2_FP | FP3 | Option A maps to FP3 (Reflective Practitioner) |
| ... | ... | ... |
| Q15_response | C | Selected option C for question 15 |
| Q15_FP | FP5 | Option C maps to FP5 (Collaboration) |
| FP1 | 4 | Used FP1 lens 4 times out of 15 (26.7%) |
| FP2 | 5 | Used FP2 lens 5 times out of 15 (33.3%) |
| FP3 | 3 | Used FP3 lens 3 times out of 15 (20.0%) |
| FP4 | 2 | Used FP4 lens 2 times out of 15 (13.3%) |
| FP5 | 1 | Used FP5 lens 1 time out of 15 (6.7%) |

**Full L01 Question-by-Question:**
```
Q1:  C → FP1  (Each Child is Unique)
Q2:  A → FP3  (Reflective Practitioner)
Q3:  C → FP1  (Each Child is Unique)
Q4:  B → FP4  (Assessment for Learning)
Q5:  D → FP1  (Each Child is Unique)
Q6:  D → FP1  (Each Child is Unique)
Q7:  D → FP3  (Reflective Practitioner)
Q8:  A → FP2  (Holistic Learning)
Q9:  C → FP2  (Holistic Learning)
Q10: A → FP2  (Holistic Learning)
Q11: B → FP3  (Reflective Practitioner)
Q12: C → FP4  (Assessment for Learning)
Q13: A → FP2  (Holistic Learning)
Q14: B → FP2  (Holistic Learning)
Q15: C → FP5  (Collaboration & Community)

Summary: FP1=4, FP2=5, FP3=3, FP4=2, FP5=1
Dominant Lens: FP2 (Holistic Learning)
Blind Spot: FP5 (Collaboration) - Only 1 usage
```

---

### Teacher Example (T001)

| Column | Value | Meaning |
|--------|-------|---------|
| user_id | T001 | Teacher 001 |
| Q1_response | D | Selected option D for question 1 |
| Q1_FP | FP5 | Option D maps to FP5 (Collaboration) |
| Q2_response | C | Selected option C for question 2 |
| Q2_FP | FP5 | Option C maps to FP5 (Collaboration) |
| ... | ... | ... |
| FP1 | 0 | Never used FP1 lens (0.0%) 🚨 BLIND SPOT |
| FP2 | 3 | Used FP2 lens 3 times (20.0%) |
| FP3 | 3 | Used FP3 lens 3 times (20.0%) |
| FP4 | 4 | Used FP4 lens 4 times (26.7%) |
| FP5 | 5 | Used FP5 lens 5 times (33.3%) - DOMINANT |

**Full T001 Question-by-Question:**
```
Q1:  D → FP5  (Collaboration)
Q2:  C → FP5  (Collaboration)
Q3:  D → FP2  (Holistic Learning)
Q4:  C → FP4  (Assessment)
Q5:  B → FP4  (Assessment)
Q6:  B → FP4  (Assessment)
Q7:  C → FP4  (Assessment)
Q8:  D → FP2  (Holistic Learning)
Q9:  D → FP2  (Holistic Learning)
Q10: D → FP3  (Reflective Practitioner)
Q11: D → FP3  (Reflective Practitioner)
Q12: B → FP3  (Reflective Practitioner)
Q13: B → FP5  (Collaboration)
Q14: B → FP5  (Collaboration)
Q15: D → FP5  (Collaboration)

Summary: FP1=0, FP2=3, FP3=3, FP4=4, FP5=5
Dominant Lens: FP5 (Collaboration)
Critical Blind Spot: FP1 (Each Child is Unique) - NEVER USED 🚨
```

---

## Use Cases

### 1. Audit & Verification
**Purpose**: Verify FP mapping logic is correct

```python
import pandas as pd

leaders = pd.read_csv('school_leaders_detailed_fp_mapping.csv')

# Verify counts match
for idx, row in leaders.iterrows():
    fp_from_questions = 0
    for q in range(1, 16):
        # Count each FP mention
        pass
    
    fp_totals = row['FP1'] + row['FP2'] + row['FP3'] + row['FP4'] + row['FP5']
    assert fp_totals == 15, f"User {row['user_id']} totals don't sum to 15"
```

### 2. Question-Level Analysis
**Purpose**: See which questions discriminate best for each FP

```python
# See what % of people selected FP1 for Q1
q1_fp_distribution = leaders['Q1_FP'].value_counts()
print(f"Q1 FP Distribution:\n{q1_fp_distribution}")

# Find questions where most people select FP1
for q in range(1, 16):
    fp1_count = (leaders[f'Q{q}_FP'] == 'FP1').sum()
    print(f"Q{q}: {fp1_count} people selected FP1 option")
```

### 3. Response Pattern Analysis
**Purpose**: Find common response patterns

```python
# Find people who always select 'A'
for idx, row in leaders.iterrows():
    responses = [row[f'Q{q}_response'] for q in range(1, 16)]
    if responses.count('A') >= 10:
        print(f"{row['user_id']} selected A {responses.count('A')} times")
```

### 4. FP Transition Analysis
**Purpose**: See how FP usage changes across questions

```python
# Track FP usage across questions
user = leaders[leaders['user_id'] == 'L01'].iloc[0]
fp_sequence = [user[f'Q{q}_FP'] for q in range(1, 16)]
print(f"FP sequence: {fp_sequence}")

# Count switches
switches = sum(1 for i in range(len(fp_sequence)-1) 
               if fp_sequence[i] != fp_sequence[i+1])
print(f"FP switches: {switches}/14 possible")
```

### 5. Create Detailed Profile Reports

```python
def generate_detailed_profile(user_row):
    report = f"User: {user_row['user_id']}\n"
    report += "="*60 + "\n\n"
    
    # Question-by-question
    report += "Question-by-Question Analysis:\n"
    report += "-"*60 + "\n"
    for q in range(1, 16):
        response = user_row[f'Q{q}_response']
        fp = user_row[f'Q{q}_FP']
        report += f"Q{q:2d}: Selected {response} → {fp}\n"
    
    # Totals
    report += "\n" + "-"*60 + "\n"
    report += "FP Distribution:\n"
    for fp in ['FP1', 'FP2', 'FP3', 'FP4', 'FP5']:
        count = user_row[fp]
        pct = (count / 15) * 100
        bar = '●' * count + '○' * (15 - count)
        report += f"{fp}: {count:2d}/15 ({pct:5.1f}%) [{bar}]\n"
    
    return report

# Use it
user = leaders[leaders['user_id'] == 'L01'].iloc[0]
print(generate_detailed_profile(user))
```

---

## Benefits of This Format

### ✅ Complete Transparency
- See exactly what each person answered (A/B/C/D)
- See exactly how each answer was classified (FP1-FP5)
- Verify mapping logic manually if needed

### ✅ Audit Trail
- Can trace back any FP count to specific questions
- Validate that totals match individual mappings
- Debug any scoring discrepancies

### ✅ Question Analysis
- Identify which questions drive FP1 usage (or lack thereof)
- See if certain questions are too easy or too hard
- Analyze response patterns across cohorts

### ✅ Individual Insights
- Understand a person's thinking progression
- See if they stick to one FP or vary
- Identify question-specific blind spots

### ✅ Flexible Analysis
- Can aggregate at any level (question, FP, user, cohort)
- Can filter by specific response patterns
- Can compare response styles across groups

---

## Python Usage Examples

### Load and Explore

```python
import pandas as pd

# Load data
leaders = pd.read_csv('school_leaders_detailed_fp_mapping.csv')
teachers = pd.read_csv('teachers_detailed_fp_mapping.csv')

# View structure
print(leaders.columns)
print(f"Leaders: {len(leaders)} rows, {len(leaders.columns)} columns")

# View first user's complete data
print(leaders.iloc[0])
```

### Find Blind Spots with Details

```python
# Find teachers with FP1 blind spot and show their Q1-Q3 responses
# (Q1-Q3 test "Each Child is Unique")
fp1_blind = teachers[teachers['FP1'] < 2].copy()

print(f"Found {len(fp1_blind)} teachers with FP1 blind spot\n")

for idx, teacher in fp1_blind.head(5).iterrows():
    print(f"Teacher: {teacher['user_id']}")
    print(f"  Q1: {teacher['Q1_response']} → {teacher['Q1_FP']}")
    print(f"  Q2: {teacher['Q2_response']} → {teacher['Q2_FP']}")
    print(f"  Q3: {teacher['Q3_response']} → {teacher['Q3_FP']}")
    print(f"  FP1 Total: {teacher['FP1']}/15\n")
```

### Compare Response Patterns

```python
# Compare leaders vs teachers on Q1
leaders_q1 = leaders['Q1_response'].value_counts()
teachers_q1 = teachers['Q1_response'].value_counts()

print("Q1 Response Distribution:")
print(f"Leaders:\n{leaders_q1}\n")
print(f"Teachers:\n{teachers_q1}\n")

# Which option leads to FP1 for Q1?
print("Q1 FP Mapping:")
sample = leaders[['Q1_response', 'Q1_FP']].drop_duplicates()
print(sample.sort_values('Q1_response'))
```

### Export Specific Views

```python
# Export just the FP mapping columns (no responses)
fp_mapping_only = leaders[['user_id'] + 
                          [f'Q{q}_FP' for q in range(1, 16)] + 
                          ['FP1', 'FP2', 'FP3', 'FP4', 'FP5']]
fp_mapping_only.to_csv('leaders_fp_mapping_only.csv', index=False)

# Export users with specific patterns
high_fp2 = leaders[leaders['FP2'] >= 6][
    ['user_id', 'Q1_response', 'Q1_FP', 'Q2_response', 'Q2_FP', 
     'FP1', 'FP2', 'FP3', 'FP4', 'FP5']
]
high_fp2.to_csv('leaders_high_fp2_detail.csv', index=False)
```

---

## Integration with Dashboard

### Recommended Dashboard Features

**1. Individual User View**
```
Display all 15 questions with:
- Question text
- User's response (A/B/C/D)
- FP that response mapped to
- Color code by FP
```

**2. Question Analysis View**
```
For each question, show:
- % of users who selected each option (A/B/C/D)
- % that resulted in each FP
- Most common FP for that question
```

**3. Pattern Detection View**
```
Identify users with:
- Same response repeated (e.g., all A's)
- No variation in FP (e.g., all FP2)
- Specific blind spots (e.g., zero FP1)
```

**4. Export Functionality**
```
Allow download of:
- Full detailed mapping
- Filtered subsets (e.g., FP1 blind spot users)
- Summary statistics
```

---

## File Statistics

| Metric | School Leaders | Teachers |
|--------|---------------|----------|
| **Rows** | 20 | 80 |
| **Columns** | 36 | 36 |
| **File Size** | ~2.5 KB | ~10 KB |
| **Format** | CSV (UTF-8) | CSV (UTF-8) |
| **Structure** | user_id + 15×(response,FP) + 5 totals | Same |

---

## Conclusion

This detailed format provides **maximum transparency and flexibility** for analysis, verification, and dashboard development. Every decision in the FP scoring process is visible and traceable.

**Key Advantage**: Unlike summary-only formats, this allows you to:
- Audit the scoring logic
- Analyze at the question level
- Understand individual thinking patterns
- Debug any discrepancies
- Create rich, detailed user profiles

---

**Format Version**: 1.0  
**Generated**: January 15, 2026  
**Coverage**: Leaders (n=20) | Teachers (n=80)  
**Questions**: 15 per user  
**FP Categories**: 5 (FP1-FP5)
