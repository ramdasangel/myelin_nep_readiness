# Regeneration: daily_progress_logging_sentiment.html

**Stage:** Micro-Intervention Comment Sentiment Analysis
**Output:** `output/daily_progress_logging_sentiment.html`
**Generator:** `scripts/build_comment_sentiment_dashboard.py`

## Overview

Self-contained HTML dashboard with keyword-based sentiment analysis on teacher daily logging comments. Supports English and Marathi (Devanagari detection). Includes word frequency, bigrams, sentiment distribution, and per-task analysis.

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only, no pip dependencies)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `assets/myelin_stat_ro/comments_full.csv` | `scripts/extract_comments.js` | Task comments with userId, taskId, submitDate, comment text |
| `output/micro_intervention_report.csv` | `scripts/micro_intervention_report.js` | User role/branch metadata |

## Step-by-Step Regeneration

### Step 1: Extract comments from prod

```bash
# SCP the script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_comments.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_comments.js > comments_output.txt 2>&1'

# Transfer the generated CSV
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/comments_full.csv \
  assets/myelin_stat_ro/comments_full.csv
```

### Step 2: Ensure micro_intervention_report.csv is up to date

If not already generated, follow Step 1 from `02_daily_progress_dashboard.md`.

### Step 3: Build the HTML dashboard

```bash
python3 scripts/build_comment_sentiment_dashboard.py
```

### Step 4: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/extract_comments.js ~/myelin_stat_ro/comments_output.txt'
```

## Output

- `output/daily_progress_logging_sentiment.html` (~626 KB, self-contained)
- Sentiment charts, word clouds, per-task analysis, comment table
- Filters to Deccan Education Society users only

## How Sentiment Analysis Works

- **Language detection:** Devanagari Unicode range detection for Marathi
- **Keyword-based scoring:** Positive/negative keyword lists for English
- **Categories:** Positive, Negative, Neutral
- No external NLP libraries — pure Python stdlib implementation

## MongoDB Collection Used

- `UserDailyProgress` — contains TasksProgress array with Comment field per task per day
