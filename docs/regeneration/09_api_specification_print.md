# Regeneration: Kshitij_Dashboard_API_Specification_print.html

**Stage:** API Specification Documentation (Print Version)
**Output:** `output/Kshitij_Dashboard_API_Specification_print.html`
**Generator:** `scripts/md_to_pdf.py`

## Overview

Print-friendly HTML version of the Kshitij Dashboard API Specification. Converts the Markdown source to styled HTML with print-optimized CSS for Cmd+P / Save as PDF.

## Prerequisites

- Python 3.x with `markdown` package (`pip install markdown`)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `output/Kshitij_Dashboard_API_Specification.md` | Manual / generated | Markdown source with API schemas, data models, metric formulas |

## Step-by-Step Regeneration

### Step 1: Update the Markdown source (if needed)

Edit `output/Kshitij_Dashboard_API_Specification.md` with any API changes.

### Step 2: Convert to HTML

```bash
python3 scripts/md_to_pdf.py
```

This reads the Markdown file and generates:
- `output/Kshitij_Dashboard_API_Specification_print.html` — styled HTML

## Output

- `output/Kshitij_Dashboard_API_Specification_print.html` (~45 KB)
- Print-friendly CSS (A4 page layout, proper margins)
- Documents all dashboard APIs, MongoDB schemas, metric formulas

## Notes

- No prod data extraction needed — this is a static documentation file
- Uses `markdown` Python package with extensions: `tables`, `fenced_code`, `toc`, `sane_lists`
- The script also attempts to generate a PDF via macOS native tools, but the HTML is the primary output
