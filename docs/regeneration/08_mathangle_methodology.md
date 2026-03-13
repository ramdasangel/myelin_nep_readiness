# Regeneration: mathangle_methodology.html

**Stage:** MathAngle Assessment Methodology Documentation
**Output:** `output/mathangle_methodology.html`
**Generator:** `scripts/mathangle_dashboard.py` (partial)

## Overview

Static HTML documentation explaining the MathAngle assessment methodology, competency areas, exit level thresholds, and indecision scoring formulas. Styled for print/PDF output.

## Prerequisites

- Python 3.x with `matplotlib` and `numpy` (`pip install matplotlib numpy`)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `/tmp/mathangle_raw.jsonl` | `scripts/extract_capacity_questions.js` | Raw assessment data (for benchmark stats) |

## Step-by-Step Regeneration

### Step 1: Ensure MathAngle data is available

Follow Steps 1 of `07_mathangle_dashboard.md` to extract `/tmp/mathangle_raw.jsonl` from prod.

### Step 2: Generate methodology documentation

```bash
python3 scripts/mathangle_dashboard.py
```

This generates:
- `output/mathangle_methodology.html` — methodology documentation
- `output/mathangle_assessment_dashboard.png` — visual summary (matplotlib)

## Output

- `output/mathangle_methodology.html` (~36 KB, self-contained)
- Explains competency areas, exit level thresholds, indecision scoring
- Styled for Cmd+P / Save as PDF

## Notes

- This is primarily a documentation/reference file, not a data dashboard
- Content is relatively static — only needs regeneration if methodology changes or benchmark stats need updating
