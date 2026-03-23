#!/usr/bin/env python3
"""Build the Comment Sentiment & Word Analytics Dashboard HTML.

Reads comments CSV extracted from UserDailyProgress, performs keyword-based
sentiment analysis on English text, detects Marathi (Devanagari) text,
and generates a self-contained interactive HTML dashboard.

No pip dependencies — stdlib only.
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
COMMENTS_CSV = BASE / "assets" / "myelin_stat_ro" / "comments_full.csv"
TASK_MAPPING_CSV = BASE / "output" / "micro_intervention_report.csv"
OUTPUT_HTML = BASE / "output" / "daily_progress_logging_sentiment.html"

# ── Task metadata (mirrors daily progress dashboard) ──
TASK_META = {
    'T01': {'label': 'Notice One Learner', 'fp': 'FP-1'},
    'T02': {'label': 'One Adjustment', 'fp': 'FP-1'},
    'T03': {'label': 'Change One Example', 'fp': 'FP-2'},
    'T04': {'label': 'Ask a Why/How', 'fp': 'FP-2'},
    'T05': {'label': 'End-of-Class Reflection', 'fp': 'FP-3'},
    'T06': {'label': 'Try One Small Change', 'fp': 'FP-3'},
    'T07': {'label': 'Quick Check', 'fp': 'FP-4'},
    'T08': {'label': 'Spot One Pattern', 'fp': 'FP-4'},
    'T09': {'label': 'Teacher Touchpoint', 'fp': 'FP-5'},
    'T10': {'label': 'Parent Signal', 'fp': 'FP-5'},
    'T11': {'label': 'Student Voice', 'fp': 'FP-1'},
    'T12': {'label': 'Pause & Name', 'fp': 'FP-4'},
}

TASKID_TO_CODE = {
    '697b1e2cc01f188423ea7e0f': 'T01', '697b1e2cc01f188423ea7e10': 'T02',
    '697b1e2cc01f188423ea7e11': 'T03', '697b1e2cc01f188423ea7e12': 'T04',
    '697b1e2cc01f188423ea7e13': 'T05', '697b1e2cc01f188423ea7e14': 'T06',
    '697b1e2cc01f188423ea7e15': 'T07', '697b1e2cc01f188423ea7e16': 'T08',
    '697b1e2cc01f188423ea7e17': 'T09', '697b1e2cc01f188423ea7e18': 'T10',
    '697b1e2cc01f188423ea7e19': 'T11', '697b1e2cc01f188423ea7e1a': 'T12',
    '697b1e3bc671c89acb64125a': 'T01', '697b1e3bc671c89acb64125b': 'T02',
    '697b1e3bc671c89acb64125c': 'T03', '697b1e3bc671c89acb64125d': 'T04',
    '697b1e3bc671c89acb64125e': 'T05', '697b1e3bc671c89acb64125f': 'T06',
    '697b1e3bc671c89acb641260': 'T07', '697b1e3bc671c89acb641261': 'T08',
    '697b1e3bc671c89acb641262': 'T09', '697b1e3bc671c89acb641263': 'T10',
    '697b1e3bc671c89acb641264': 'T11', '697b1e3bc671c89acb641265': 'T12',
}

FP_COLORS = {
    'FP-1': '#6366f1', 'FP-2': '#ec4899', 'FP-3': '#f59e0b',
    'FP-4': '#10b981', 'FP-5': '#3b82f6',
}

# ── Sentiment lexicon (education domain) ──
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'wonderful', 'amazing', 'awesome', 'fantastic',
    'helpful', 'useful', 'effective', 'productive', 'successful', 'improved',
    'improvement', 'progress', 'better', 'best', 'love', 'loved', 'enjoy',
    'enjoyed', 'interesting', 'excited', 'exciting', 'happy', 'glad', 'pleased',
    'confident', 'motivated', 'inspired', 'creative', 'engaged', 'engaging',
    'positive', 'clear', 'understand', 'understood', 'learned', 'learning',
    'active', 'actively', 'participated', 'participation', 'responsive',
    'cooperative', 'collaborative', 'attentive', 'focused', 'enthusiastic',
    'encouraged', 'supportive', 'well', 'nice', 'beautiful', 'brilliant',
    'outstanding', 'remarkable', 'impressive', 'perfect', 'satisfied',
    'comfortable', 'easy', 'smoothly', 'smooth', 'completed', 'achieved',
    'achievement', 'growth', 'developing', 'enhanced', 'benefited', 'benefit',
    'yes', 'done', 'try', 'tried', 'observed', 'noticed', 'reflected',
    'applied', 'practiced', 'implemented', 'adapted', 'adjusted', 'modified',
    'changed', 'different', 'new', 'innovative', 'thoughtful', 'insightful',
}

NEGATIVE_WORDS = {
    'bad', 'poor', 'terrible', 'horrible', 'awful', 'worst', 'difficult',
    'hard', 'struggle', 'struggled', 'struggling', 'challenge', 'challenging',
    'problem', 'problems', 'issue', 'issues', 'concern', 'concerned',
    'confused', 'confusing', 'confusion', 'unclear', 'difficult', 'boring',
    'bored', 'frustrating', 'frustrated', 'disappointing', 'disappointed',
    'failed', 'failure', 'unable', 'cannot', 'impossible', 'weak',
    'weakness', 'lacking', 'missing', 'absent', 'incomplete', 'wrong',
    'mistake', 'error', 'not', 'no', 'never', 'nothing', 'none',
    'unhappy', 'sad', 'worried', 'anxious', 'stress', 'stressed',
    'tired', 'exhausted', 'late', 'slow', 'behind', 'gap', 'gaps',
    'distracted', 'disruptive', 'unresponsive', 'passive', 'reluctant',
    'resist', 'resistance', 'dropout', 'dropped',
}

NEGATION_WORDS = {'not', 'no', "don't", "doesn't", "didn't", "won't", "can't",
                  "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't",
                  'never', 'neither', 'nor', 'hardly', 'barely', 'scarcely'}

# ── Marathi sentiment lexicon (education domain) ──
MARATHI_POSITIVE = {
    # Praise / appreciation
    'छान', 'उत्तम', 'सुंदर', 'अप्रतिम', 'चांगले', 'चांगला', 'चांगली',
    'कौतुक', 'शाबासकी', 'दाद', 'प्रोत्साहन', 'प्रेरणा',
    # Engagement / effort
    'उत्साह', 'उत्साही', 'उत्साहाने', 'सहभागी', 'सहभाग', 'सक्रिय',
    'प्रयत्न', 'प्रतिसाद', 'एकाग्र', 'एकाग्रता', 'एकाग्रचिताने',
    'स्थिर', 'शांत', 'लक्षपूर्वक', 'आवडले', 'आवड',
    # Learning / improvement
    'सुधारणा', 'प्रगती', 'बदल', 'विकास', 'शिकले', 'समजले', 'समजला',
    'आकलन', 'आत्मसात', 'लक्षात', 'आनंद', 'आनंदी', 'खुश', 'समाधान',
    'समाधानी', 'यशस्वी', 'यश',
    # Positive action
    'सहकार्य', 'मदत', 'मार्गदर्शन', 'स्वतंत्र', 'स्वतःहून',
    'आत्मविश्वास', 'उत्तरे', 'तयार', 'वाचन', 'विविध',
    'सर्जनशील', 'कल्पकता', 'रुची', 'वाढते', 'वाढली',
}

MARATHI_NEGATIVE = {
    # Difficulty / struggle
    'अडचण', 'अडचणी', 'कठीण', 'अवघड', 'समस्या', 'त्रास',
    # Absence / non-engagement
    'अनुपस्थित', 'गैरहजर', 'दुर्लक्ष', 'निष्काळजी',
    # Poor performance
    'चुका', 'चूक', 'अपूर्ण', 'कमकुवत', 'कमजोर',
    # Negative behavior
    'अस्थिर', 'अशांत', 'भांडण', 'तक्रार', 'भीती',
    # Inability
    'शकत', 'शकला', 'शकली',  # often with नाही
    'नकार', 'नकारात्मक', 'दुरुस्त', 'वाईट',
}

MARATHI_NEGATION = {'नाही', 'नव्हते', 'नव्हती', 'नव्हता', 'नको', 'नसते', 'नसतो',
                    'नसती', 'कधीच', 'अजिबात'}

MARATHI_STOP_WORDS = {
    'आज', 'व', 'आणि', 'तो', 'ती', 'ते', 'या', 'हा', 'ही', 'हे',
    'त्या', 'त्याला', 'त्याने', 'त्यांनी', 'त्यामुळे', 'त्यांचे',
    'मी', 'मला', 'माझे', 'माझा', 'माझी', 'आम्ही', 'आमचे',
    'एक', 'एका', 'दोन', 'तीन', 'सर्व', 'काही', 'पण', 'तसेच',
    'करून', 'करत', 'केले', 'केली', 'केला', 'होता', 'होती', 'होते',
    'आहे', 'आहेत', 'होते', 'असे', 'म्हणून', 'वर', 'मध्ये',
    'च्या', 'ला', 'ने', 'चे', 'ची', 'चा', 'पासून', 'साठी',
    'किंवा', 'परंतु', 'जर', 'तर', 'कसे', 'काय', 'कोण',
    'झाली', 'झाले', 'झाला', 'दिली', 'दिले', 'दिला',
    'असा', 'अशी', 'अशा', 'खूप', 'अधिक', 'कमी',
}

STOP_WORDS = {
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'she', 'it', 'its',
    'they', 'them', 'their', 'this', 'that', 'these', 'those', 'is', 'am',
    'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'may', 'might',
    'can', 'could', 'a', 'an', 'the', 'and', 'but', 'or', 'if', 'of', 'at',
    'by', 'for', 'with', 'about', 'to', 'from', 'in', 'on', 'up', 'out',
    'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'under', 'over', 'then', 'than', 'so', 'very', 'just',
    'also', 'too', 'here', 'there', 'when', 'where', 'how', 'what',
    'which', 'who', 'whom', 'why', 'all', 'each', 'every', 'both',
    'some', 'any', 'few', 'more', 'most', 'other', 'such', 'only',
    'same', 'own', 'as', 'while', 'because', 'since', 'until',
    'although', 'though', 'whether', 'either', 'nor', 'once',
}

# Devanagari Unicode range for Marathi detection
DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')
GARBAGE_RE = re.compile(r'^(.)\1{2,}$')  # e.g. "aaaa", "xxx"
TEST_PATTERNS = {'test', 'testing', 'asdf', 'qwerty', 'abc', 'xyz', '123', 'aaa', 'bbb'}


def detect_language(text):
    """Return 'marathi' if text contains Devanagari chars, else 'english'."""
    devanagari_count = len(DEVANAGARI_RE.findall(text))
    if devanagari_count >= 2:
        return 'marathi'
    return 'english'


def is_garbage(text):
    """Filter out garbage: too short, repeated chars, test patterns."""
    t = text.strip().lower()
    if len(t) < 3:
        return True
    if GARBAGE_RE.match(t):
        return True
    if t in TEST_PATTERNS:
        return True
    return False


def score_sentiment(text):
    """Score English text sentiment using keyword lexicon with negation window.
    Returns (label, score) where score is in [-1, 1] range.
    """
    tokens = re.findall(r"[a-z']+", text.lower())
    if not tokens:
        return ('neutral', 0.0)

    pos_count = 0
    neg_count = 0

    for i, token in enumerate(tokens):
        # Check negation window (3 tokens before)
        negated = False
        for j in range(max(0, i - 3), i):
            if tokens[j] in NEGATION_WORDS:
                negated = True
                break

        if token in POSITIVE_WORDS:
            if negated:
                neg_count += 1
            else:
                pos_count += 1
        elif token in NEGATIVE_WORDS:
            if negated:
                pos_count += 1
            else:
                neg_count += 1

    total = pos_count + neg_count
    if total == 0:
        return ('neutral', 0.0)

    score = (pos_count - neg_count) / total
    if score > 0.1:
        return ('positive', round(score, 2))
    elif score < -0.1:
        return ('negative', round(score, 2))
    else:
        return ('neutral', round(score, 2))


def score_sentiment_marathi(text):
    """Score Marathi text sentiment using Devanagari keyword lexicon with negation.
    Returns (label, score) where score is in [-1, 1] range.
    """
    tokens = re.findall(r'[\u0900-\u097F]+', text)
    if not tokens:
        return ('neutral', 0.0)

    pos_count = 0
    neg_count = 0

    for i, token in enumerate(tokens):
        negated = False
        for j in range(max(0, i - 3), i):
            if tokens[j] in MARATHI_NEGATION:
                negated = True
                break
        # Also check if नाही follows within 2 tokens (post-negation in Marathi)
        for j in range(i + 1, min(len(tokens), i + 3)):
            if tokens[j] in MARATHI_NEGATION:
                negated = True
                break

        if token in MARATHI_POSITIVE:
            if negated:
                neg_count += 1
            else:
                pos_count += 1
        elif token in MARATHI_NEGATIVE:
            if negated:
                pos_count += 1
            else:
                neg_count += 1

    total = pos_count + neg_count
    if total == 0:
        return ('neutral', 0.0)

    score = (pos_count - neg_count) / total
    if score > 0.1:
        return ('positive', round(score, 2))
    elif score < -0.1:
        return ('negative', round(score, 2))
    else:
        return ('neutral', round(score, 2))


def tokenize_for_words(text):
    """Tokenize English text, remove stop words, return list of words."""
    tokens = re.findall(r"[a-z']+", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1 and not t.startswith("'")]


def tokenize_marathi(text):
    """Tokenize Marathi text, remove stop words."""
    tokens = re.findall(r'[\u0900-\u097F]+', text)
    return [t for t in tokens if t not in MARATHI_STOP_WORDS and len(t) > 1]


def extract_bigrams(text):
    """Extract bigrams from tokenized English text."""
    words = tokenize_for_words(text)
    return [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]


def extract_bigrams_marathi(text):
    """Extract bigrams from tokenized Marathi text."""
    words = tokenize_marathi(text)
    return [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]


# ── Step 1: Load user metadata from task mapping report ──
print("Loading user metadata...")
user_meta = {}
if TASK_MAPPING_CSV.exists():
    with open(TASK_MAPPING_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            uid = row['UserId'].strip()
            user_meta[uid] = {
                'name': row.get('FullName', '').strip() or f"{row.get('FirstName','')} {row.get('LastName','')}".strip(),
                'role': row.get('Role', '').strip(),
                'branch': row.get('BranchName', '').strip(),
                'school': row.get('SchoolName', '').strip(),
            }

# ── Step 2: Load & process comments ──
print(f"Reading comments from {COMMENTS_CSV}...")
comments = []
with open(COMMENTS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        text = row['comment'].strip()
        if is_garbage(text):
            continue
        task_id = row['taskId'].strip()
        task_code = TASKID_TO_CODE.get(task_id, '')
        uid = row['userId'].strip()
        meta = user_meta.get(uid, {})

        # Filter: keep only Deccan Education Society users
        school = meta.get('school', '')
        if school != 'Deccan Education Society':
            continue

        lang = detect_language(text)
        if lang == 'english':
            label, score = score_sentiment(text)
        else:
            label, score = score_sentiment_marathi(text)

        comments.append({
            'userId': uid,
            'name': meta.get('name', ''),
            'role': meta.get('role', ''),
            'branch': meta.get('branch', ''),
            'school': meta.get('school', ''),
            'submitDate': row['submitDate'].strip(),
            'createdAt': row.get('createdAt', '').strip(),
            'taskId': task_id,
            'taskCode': task_code,
            'isChecked': row['isChecked'].strip(),
            'comment': text,
            'language': lang,
            'sentiment': label,
            'score': score,
        })

print(f"  {len(comments)} valid comments loaded")

# ── Step 3: Compute aggregates ──
total_comments = len(comments)
english_comments = [c for c in comments if c['language'] == 'english']
marathi_comments = [c for c in comments if c['language'] == 'marathi']
# Sentiment across ALL comments (both languages now scored)
positive = [c for c in comments if c['sentiment'] == 'positive']
negative = [c for c in comments if c['sentiment'] == 'negative']
neutral = [c for c in comments if c['sentiment'] == 'neutral']
unique_users = set(c['userId'] for c in comments)
avg_comments_per_user = round(total_comments / len(unique_users), 1) if unique_users else 0

pos_pct = round(len(positive) / total_comments * 100, 1) if total_comments else 0
neg_pct = round(len(negative) / total_comments * 100, 1) if total_comments else 0
neu_pct = round(len(neutral) / total_comments * 100, 1) if total_comments else 0

# Per-language sentiment breakdown
en_positive = [c for c in english_comments if c['sentiment'] == 'positive']
en_negative = [c for c in english_comments if c['sentiment'] == 'negative']
en_neutral = [c for c in english_comments if c['sentiment'] == 'neutral']
mr_positive = [c for c in marathi_comments if c['sentiment'] == 'positive']
mr_negative = [c for c in marathi_comments if c['sentiment'] == 'negative']
mr_neutral = [c for c in marathi_comments if c['sentiment'] == 'neutral']

# Sentiment over time
dates_all = sorted(set(c['submitDate'] for c in comments if c['submitDate']))
sentiment_by_date = defaultdict(lambda: {'positive': 0, 'neutral': 0, 'negative': 0})
for c in comments:
    if c['submitDate']:
        sentiment_by_date[c['submitDate']][c['sentiment']] += 1

# Cumulative sentiment score over time (all languages)
cumulative_scores = []
running_sum = 0
running_count = 0
for d in dates_all:
    for c in comments:
        if c['submitDate'] == d:
            running_sum += c['score']
            running_count += 1
    cumulative_scores.append(round(running_sum / running_count, 3) if running_count else 0)

# Word frequency — English
en_word_counter = Counter()
en_bigram_counter = Counter()
for c in english_comments:
    en_word_counter.update(tokenize_for_words(c['comment']))
    en_bigram_counter.update(extract_bigrams(c['comment']))

top_en_words = en_word_counter.most_common(25)
top_en_bigrams = en_bigram_counter.most_common(15)

# Word frequency — Marathi
mr_word_counter = Counter()
mr_bigram_counter = Counter()
for c in marathi_comments:
    mr_word_counter.update(tokenize_marathi(c['comment']))
    mr_bigram_counter.update(extract_bigrams_marathi(c['comment']))

top_mr_words = mr_word_counter.most_common(25)
top_mr_bigrams = mr_bigram_counter.most_common(15)

# Per-task analysis
task_comment_count = Counter()
task_sentiment = defaultdict(lambda: {'positive': 0, 'neutral': 0, 'negative': 0})
for c in comments:
    tc = c['taskCode'] or 'Unknown'
    task_comment_count[tc] += 1
    task_sentiment[tc][c['sentiment']] += 1

task_codes_sorted = sorted([tc for tc in task_comment_count.keys() if tc.startswith('T')],
                           key=lambda x: int(x[1:]))
if 'Unknown' in task_comment_count:
    task_codes_sorted.append('Unknown')

# Common text patterns
normalized_comments = defaultdict(lambda: {'count': 0, 'users': set(), 'tasks': set(), 'scores': [], 'lang': ''})
for c in comments:
    norm = c['comment'].strip().lower()
    nc = normalized_comments[norm]
    nc['count'] += 1
    nc['users'].add(c['userId'])
    nc['tasks'].add(c['taskCode'] or '?')
    nc['scores'].append(c['score'])
    nc['lang'] = c['language']
top_patterns = sorted(normalized_comments.items(), key=lambda x: -x[1]['count'])[:20]

# Word cloud data — combined (top 60 Marathi + top 20 English)
cloud_mr = mr_word_counter.most_common(60)
cloud_en = en_word_counter.most_common(20)
cloud_words_all = cloud_mr + cloud_en
max_freq = cloud_words_all[0][1] if cloud_words_all else 1

# ── Day labels ──
DAY_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
from datetime import date as dt_date
date_labels = []
for d in dates_all:
    try:
        dobj = dt_date.fromisoformat(d)
        date_labels.append(f"{d.replace('2026-','')} {DAY_ABBR[dobj.weekday()]}")
    except ValueError:
        date_labels.append(d)

# ── Build HTML ──
print("Generating HTML dashboard...")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comment Sentiment &amp; Word Analytics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {{
  --primary: #1a365d; --accent: #2b6cb0; --green: #38a169; --amber: #d69e2e;
  --orange: #ed8936; --red: #e53e3e; --bg: #f7fafc; --card: #ffffff;
  --border: #e2e8f0; --text: #2d3748; --muted: #718096; --light: #ebf4ff;
  --fp1: #6366f1; --fp2: #ec4899; --fp3: #f59e0b; --fp4: #10b981; --fp5: #3b82f6;
  --positive: #38a169; --neutral: #d69e2e; --negative: #e53e3e; --marathi: #805ad5;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }}
.header {{ background: linear-gradient(135deg, #742a2a, #e53e3e); color: white; padding: 24px 32px; }}
.header h1 {{ font-size: 22px; margin-bottom: 4px; }}
.header p {{ font-size: 13px; opacity: 0.85; }}
.container {{ max-width: 1500px; margin: 0 auto; padding: 24px; }}
.kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 12px; margin-bottom: 24px; }}
.kpi {{ background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-top: 4px solid var(--accent); }}
.kpi .value {{ font-size: 30px; font-weight: 800; color: var(--primary); }}
.kpi .label {{ font-size: 11px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
.kpi.green {{ border-top-color: var(--green); }} .kpi.green .value {{ color: var(--green); }}
.kpi.amber {{ border-top-color: var(--amber); }} .kpi.amber .value {{ color: var(--amber); }}
.kpi.orange {{ border-top-color: var(--orange); }} .kpi.orange .value {{ color: var(--orange); }}
.kpi.red {{ border-top-color: var(--red); }} .kpi.red .value {{ color: var(--red); }}
.kpi.purple {{ border-top-color: var(--marathi); }} .kpi.purple .value {{ color: var(--marathi); }}
.chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
.chart-box {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.chart-box h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
.chart-box canvas {{ max-height: 340px; }}
.chart-box.full {{ grid-column: 1 / -1; }}
.section-title {{ font-size: 16px; font-weight: 700; color: var(--primary); margin: 24px 0 12px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }}
.filter-bar {{ background: white; border: 1px solid var(--border); border-radius: 8px; padding: 14px 20px; margin-bottom: 20px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
.filter-bar label {{ font-weight: 600; font-size: 13px; color: var(--primary); }}
.filter-bar select, .filter-bar input {{ padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; }}
.filter-bar input[type="text"] {{ min-width: 200px; }}
.filter-bar .count-badge {{ margin-left: auto; background: var(--light); padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; color: var(--accent); }}
.table-section {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; overflow-x: auto; }}
.table-section h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
table.data {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
table.data th {{ background: var(--primary); color: white; padding: 8px 10px; text-align: left; white-space: nowrap; cursor: pointer; user-select: none; position: sticky; top: 0; font-size: 10px; }}
table.data th:hover {{ background: var(--accent); }}
table.data td {{ padding: 6px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
table.data tr:hover {{ background: var(--light); }}
table.data tr:nth-child(even) {{ background: #f8fafc; }}
table.data tr:nth-child(even):hover {{ background: var(--light); }}
.sentiment-badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 10px; font-weight: 700; }}
.sent-positive {{ background: #f0fff4; color: var(--green); }}
.sent-neutral {{ background: #fffbeb; color: var(--amber); }}
.sent-negative {{ background: #fff5f5; color: var(--red); }}
.sent-marathi {{ background: #faf5ff; color: var(--marathi); }}
.word-cloud {{ background: white; border-radius: 12px; padding: 24px 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; line-height: 2.2; text-align: center; }}
.word-cloud span {{ display: inline-block; margin: 2px 6px; transition: transform 0.2s; cursor: default; }}
.word-cloud span:hover {{ transform: scale(1.15); }}
.pattern-table {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; overflow-x: auto; }}
.pattern-table h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
.fp-tag {{ display: inline-block; padding: 2px 6px; border-radius: 10px; font-size: 9px; font-weight: 700; margin: 1px; white-space: nowrap; }}
.fp-tag.fp1 {{ background: #eef2ff; color: var(--fp1); }} .fp-tag.fp2 {{ background: #fdf2f8; color: var(--fp2); }}
.fp-tag.fp3 {{ background: #fffbeb; color: var(--fp3); }} .fp-tag.fp4 {{ background: #ecfdf5; color: var(--fp4); }}
.fp-tag.fp5 {{ background: #eff6ff; color: var(--fp5); }}
@media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>Comment Sentiment &amp; Word Analytics Dashboard</h1>
  <p>Daily Progress Comments &nbsp;|&nbsp; {total_comments} Comments &nbsp;|&nbsp; {len(unique_users)} Users &nbsp;|&nbsp; Data through 2026-02-23</p>
</div>
<div class="container">

<!-- Section 1: KPI Row -->
<div class="kpi-row">
  <div class="kpi"><div class="value">{total_comments}</div><div class="label">Total Comments</div></div>
  <div class="kpi"><div class="value">{len(english_comments)}</div><div class="label">English</div></div>
  <div class="kpi purple"><div class="value">{len(marathi_comments)}</div><div class="label">Marathi</div></div>
  <div class="kpi green"><div class="value">{pos_pct}%</div><div class="label">Positive (All)</div></div>
  <div class="kpi amber"><div class="value">{neu_pct}%</div><div class="label">Neutral (All)</div></div>
  <div class="kpi red"><div class="value">{neg_pct}%</div><div class="label">Negative (All)</div></div>
  <div class="kpi"><div class="value">{len(unique_users)}</div><div class="label">Users Who Commented</div></div>
  <div class="kpi orange"><div class="value">{avg_comments_per_user}</div><div class="label">Avg Comments/User</div></div>
</div>

<!-- Section 2: Sentiment Charts -->
<div class="section-title">Sentiment Analysis (English + Marathi)</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Overall Sentiment Distribution</h3><canvas id="chartSentimentDonut"></canvas></div>
  <div class="chart-box"><h3>Sentiment Over Time (All Languages)</h3><canvas id="chartSentimentTime"></canvas></div>
</div>
<div class="chart-grid">
  <div class="chart-box"><h3>English Sentiment Breakdown</h3><canvas id="chartSentimentEN"></canvas></div>
  <div class="chart-box"><h3>Marathi Sentiment Breakdown</h3><canvas id="chartSentimentMR"></canvas></div>
</div>

<!-- Section 3: Word Analytics -->
<div class="section-title">Word Analytics — Marathi</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Top 25 Marathi Words</h3><canvas id="chartTopWordsMR"></canvas></div>
  <div class="chart-box"><h3>Top 15 Marathi Bigrams</h3><canvas id="chartBigramsMR"></canvas></div>
</div>
<div class="section-title">Word Analytics — English</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Top 25 English Words</h3><canvas id="chartTopWords"></canvas></div>
  <div class="chart-box"><h3>Top 15 English Bigrams</h3><canvas id="chartBigrams"></canvas></div>
</div>

<!-- Section 4: Per-Task Analysis -->
<div class="section-title">Per-Task Analysis</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Comment Count by Task</h3><canvas id="chartTaskComments"></canvas></div>
  <div class="chart-box"><h3>Sentiment by Task (Stacked %)</h3><canvas id="chartTaskSentiment"></canvas></div>
</div>

<!-- Section 5: Word Cloud -->
<div class="section-title">Word Cloud (Marathi + English)</div>
<div class="word-cloud">
"""

# Generate word cloud spans
for word, freq in cloud_words_all:
    # Font size: 12–48px proportional to frequency
    size = max(12, min(48, int(12 + 36 * (freq / max_freq))))
    # Color from FP palette rotation
    palette = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#e53e3e', '#d69e2e', '#805ad5']
    color = palette[hash(word) % len(palette)]
    opacity = max(0.55, min(1.0, 0.55 + 0.45 * (freq / max_freq)))
    html += f'<span style="font-size:{size}px;color:{color};opacity:{opacity}" title="{word}: {freq}">{word}</span>\n'

html += "</div>\n"

# Section 6: Common Text Patterns
html += """
<div class="section-title">Common Text Patterns</div>
<div class="pattern-table">
<h3>Top 20 Most-Repeated Normalized Comments</h3>
<table class="data">
<thead><tr><th>#</th><th>Comment Text</th><th>Count</th><th>Users</th><th>Tasks</th><th>Avg Score</th></tr></thead>
<tbody>
"""
for i, (text, info) in enumerate(top_patterns):
    avg_s = round(sum(info['scores']) / len(info['scores']), 2) if info['scores'] else 0
    tasks_str = ', '.join(sorted(info['tasks']))
    display_text = text[:100] + ('...' if len(text) > 100 else '')
    # Escape HTML
    display_text = display_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html += f"<tr><td>{i+1}</td><td style='max-width:400px;word-break:break-word'>{display_text}</td>"
    html += f"<td style='text-align:center'><b>{info['count']}</b></td>"
    html += f"<td style='text-align:center'>{len(info['users'])}</td>"
    html += f"<td style='font-size:10px'>{tasks_str}</td>"
    if avg_s > 0.1:
        html += f"<td style='text-align:center;color:var(--green)'>{avg_s}</td>"
    elif avg_s < -0.1:
        html += f"<td style='text-align:center;color:var(--red)'>{avg_s}</td>"
    else:
        html += f"<td style='text-align:center;color:var(--amber)'>{avg_s}</td>"
    html += "</tr>\n"

html += "</tbody></table></div>\n"

# Section 7: Comment Detail Table
# Build unique values for filter dropdowns
roles = sorted(set(c['role'] for c in comments if c['role']))
sentiments = ['positive', 'neutral', 'negative', 'marathi']
languages = ['english', 'marathi']
task_options = sorted(set(c['taskCode'] for c in comments if c['taskCode']))

html += """
<div class="section-title">Comment Detail Table</div>
<div class="filter-bar">
  <label>Filter:</label>
  <input type="text" id="filterSearch" placeholder="Search comment, name, branch..." oninput="applyFilters()">
  <select id="filterRole" onchange="applyFilters()"><option value="">All Roles</option>"""
for r in roles:
    html += f'<option value="{r}">{r}</option>'
html += """</select>
  <select id="filterSentiment" onchange="applyFilters()"><option value="">All Sentiment</option>
    <option value="positive">Positive</option><option value="neutral">Neutral</option>
    <option value="negative">Negative</option></select>
  <select id="filterLang" onchange="applyFilters()"><option value="">All Languages</option>
    <option value="english">English</option><option value="marathi">Marathi</option></select>
  <select id="filterTask" onchange="applyFilters()"><option value="">All Tasks</option>"""
for tc in task_options:
    lbl = TASK_META.get(tc, {}).get('label', tc)
    html += f'<option value="{tc}">{tc} {lbl}</option>'
html += """</select>
  <span class="count-badge" id="filteredCount"></span>
</div>
"""

html += """
<div class="table-section">
<table class="data" id="commentTable">
<thead><tr>
  <th onclick="sortTable(0)">#</th>
  <th onclick="sortTable(1)">User</th>
  <th onclick="sortTable(2)">Role</th>
  <th onclick="sortTable(3)">Branch</th>
  <th onclick="sortTable(4)">Task</th>
  <th onclick="sortTable(5)">Date</th>
  <th onclick="sortTable(6)">Comment</th>
  <th onclick="sortTable(7)">Language</th>
  <th onclick="sortTable(8)">Sentiment</th>
  <th onclick="sortTable(9)">Score</th>
</tr></thead>
<tbody id="commentTableBody">
"""

for i, c in enumerate(comments):
    name_esc = (c['name'] or c['userId'][:8]).replace('&', '&amp;').replace('<', '&lt;')
    comment_esc = c['comment'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    if len(comment_esc) > 150:
        comment_esc = comment_esc[:150] + '...'
    task_label = c['taskCode']
    sent_cls = f"sent-{c['sentiment']}"
    score_color = 'var(--green)' if c['score'] > 0.1 else ('var(--red)' if c['score'] < -0.1 else 'var(--amber)')

    html += f"""<tr data-name="{(c['name'] or '').lower()}" data-role="{c['role']}" data-branch="{c['branch'].lower()}" data-sentiment="{c['sentiment']}" data-lang="{c['language']}" data-task="{c['taskCode']}" data-comment="{c['comment'][:200].lower().replace('"','&quot;')}">
  <td>{i+1}</td>
  <td><b>{name_esc}</b></td>
  <td>{c['role']}</td>
  <td style="max-width:150px;font-size:10px">{c['branch']}</td>
  <td style="white-space:nowrap">{task_label}</td>
  <td style="white-space:nowrap;font-size:10px">{c['submitDate'].replace('2026-','')}</td>
  <td style="max-width:300px;word-break:break-word;font-size:10px">{comment_esc}</td>
  <td style="font-size:10px">{c['language']}</td>
  <td><span class="sentiment-badge {sent_cls}">{c['sentiment']}</span></td>
  <td style="text-align:center;color:{score_color};font-weight:700">{c['score']}</td>
</tr>"""

html += "</tbody></table></div>\n"

# ── JavaScript for Charts & Interactivity ──
html += f"""
<script>
// Overall Sentiment Donut (all languages scored)
new Chart(document.getElementById('chartSentimentDonut'), {{
  type: 'doughnut',
  data: {{
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{{
      data: [{len(positive)}, {len(neutral)}, {len(negative)}],
      backgroundColor: ['#38a169', '#d69e2e', '#e53e3e'],
      borderWidth: 2, borderColor: '#fff'
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'right' }},
      tooltip: {{ callbacks: {{
        label: function(ctx) {{
          const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
          const pct = (ctx.parsed / total * 100).toFixed(1);
          return ctx.label + ': ' + ctx.parsed + ' (' + pct + '%)';
        }}
      }} }}
    }}
  }}
}});

// Sentiment Over Time (all languages)
new Chart(document.getElementById('chartSentimentTime'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(date_labels)},
    datasets: [
      {{ label: 'Positive', data: {json.dumps([sentiment_by_date[d]['positive'] for d in dates_all])}, backgroundColor: '#38a169', borderRadius: 2, order: 2 }},
      {{ label: 'Neutral', data: {json.dumps([sentiment_by_date[d]['neutral'] for d in dates_all])}, backgroundColor: '#d69e2e', borderRadius: 2, order: 3 }},
      {{ label: 'Negative', data: {json.dumps([sentiment_by_date[d]['negative'] for d in dates_all])}, backgroundColor: '#e53e3e', borderRadius: 2, order: 4 }},
      {{ label: 'Cumulative Avg Score', data: {json.dumps(cumulative_scores)}, type: 'line', borderColor: '#2b6cb0', pointBackgroundColor: '#2b6cb0', borderWidth: 2, tension: 0.3, yAxisID: 'y1', order: 1 }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ stacked: true }},
      y: {{ stacked: true, title: {{ display: true, text: 'Comments' }}, beginAtZero: true }},
      y1: {{ position: 'right', title: {{ display: true, text: 'Avg Score' }}, min: -1, max: 1, grid: {{ drawOnChartArea: false }} }}
    }}
  }}
}});

// English Sentiment Breakdown
new Chart(document.getElementById('chartSentimentEN'), {{
  type: 'doughnut',
  data: {{
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{{
      data: [{len(en_positive)}, {len(en_neutral)}, {len(en_negative)}],
      backgroundColor: ['#38a169', '#d69e2e', '#e53e3e'],
      borderWidth: 2, borderColor: '#fff'
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      title: {{ display: true, text: '{len(english_comments)} English comments' }},
      legend: {{ position: 'bottom' }},
      tooltip: {{ callbacks: {{
        label: function(ctx) {{
          const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
          const pct = (ctx.parsed / total * 100).toFixed(1);
          return ctx.label + ': ' + ctx.parsed + ' (' + pct + '%)';
        }}
      }} }}
    }}
  }}
}});

// Marathi Sentiment Breakdown
new Chart(document.getElementById('chartSentimentMR'), {{
  type: 'doughnut',
  data: {{
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{{
      data: [{len(mr_positive)}, {len(mr_neutral)}, {len(mr_negative)}],
      backgroundColor: ['#38a169', '#d69e2e', '#e53e3e'],
      borderWidth: 2, borderColor: '#fff'
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      title: {{ display: true, text: '{len(marathi_comments)} Marathi comments' }},
      legend: {{ position: 'bottom' }},
      tooltip: {{ callbacks: {{
        label: function(ctx) {{
          const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
          const pct = (ctx.parsed / total * 100).toFixed(1);
          return ctx.label + ': ' + ctx.parsed + ' (' + pct + '%)';
        }}
      }} }}
    }}
  }}
}});

// Top 25 Marathi Words
new Chart(document.getElementById('chartTopWordsMR'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([w for w, _ in top_mr_words])},
    datasets: [{{ label: 'Frequency', data: {json.dumps([c for _, c in top_mr_words])}, backgroundColor: '#805ad5', borderRadius: 3 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ title: {{ display: true, text: 'Count' }} }} }} }}
}});

// Top 15 Marathi Bigrams
new Chart(document.getElementById('chartBigramsMR'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([b for b, _ in top_mr_bigrams])},
    datasets: [{{ label: 'Frequency', data: {json.dumps([c for _, c in top_mr_bigrams])}, backgroundColor: '#b794f4', borderRadius: 3 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ title: {{ display: true, text: 'Count' }} }} }} }}
}});

// Top 25 English Words
new Chart(document.getElementById('chartTopWords'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([w for w, _ in top_en_words])},
    datasets: [{{ label: 'Frequency', data: {json.dumps([c for _, c in top_en_words])}, backgroundColor: '#6366f1', borderRadius: 3 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ title: {{ display: true, text: 'Count' }} }} }} }}
}});

// Top 15 English Bigrams
new Chart(document.getElementById('chartBigrams'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([b for b, _ in top_en_bigrams])},
    datasets: [{{ label: 'Frequency', data: {json.dumps([c for _, c in top_en_bigrams])}, backgroundColor: '#ec4899', borderRadius: 3 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ title: {{ display: true, text: 'Count' }} }} }} }}
}});

// Comment Count by Task
new Chart(document.getElementById('chartTaskComments'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([f"{tc} {TASK_META.get(tc, {}).get('label', tc)}" for tc in task_codes_sorted])},
    datasets: [{{
      label: 'Comments',
      data: {json.dumps([task_comment_count.get(tc, 0) for tc in task_codes_sorted])},
      backgroundColor: {json.dumps([FP_COLORS.get(TASK_META.get(tc, {}).get('fp', ''), '#94a3b8') for tc in task_codes_sorted])},
      borderRadius: 4
    }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ title: {{ display: true, text: 'Comments' }} }} }} }}
}});

// Sentiment by Task (Stacked %)
const taskSentData = {json.dumps({tc: task_sentiment[tc] for tc in task_codes_sorted})};
const taskLabels = {json.dumps([f"{tc} {TASK_META.get(tc, {}).get('label', tc)}" for tc in task_codes_sorted])};
const taskTotals = taskLabels.map((_, i) => {{
  const tc = {json.dumps(task_codes_sorted)}[i];
  const s = taskSentData[tc];
  return (s.positive || 0) + (s.neutral || 0) + (s.negative || 0);
}});

new Chart(document.getElementById('chartTaskSentiment'), {{
  type: 'bar',
  data: {{
    labels: taskLabels,
    datasets: [
      {{ label: 'Positive %', data: taskLabels.map((_, i) => {{ const tc = {json.dumps(task_codes_sorted)}[i]; return taskTotals[i] ? Math.round((taskSentData[tc].positive || 0) / taskTotals[i] * 100) : 0; }}), backgroundColor: '#38a169', borderRadius: 2 }},
      {{ label: 'Neutral %', data: taskLabels.map((_, i) => {{ const tc = {json.dumps(task_codes_sorted)}[i]; return taskTotals[i] ? Math.round((taskSentData[tc].neutral || 0) / taskTotals[i] * 100) : 0; }}), backgroundColor: '#d69e2e', borderRadius: 2 }},
      {{ label: 'Negative %', data: taskLabels.map((_, i) => {{ const tc = {json.dumps(task_codes_sorted)}[i]; return taskTotals[i] ? Math.round((taskSentData[tc].negative || 0) / taskTotals[i] * 100) : 0; }}), backgroundColor: '#e53e3e', borderRadius: 2 }}
    ]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{ x: {{ stacked: true, max: 100, title: {{ display: true, text: '%' }} }}, y: {{ stacked: true }} }}
  }}
}});

// Table Filter
function applyFilters() {{
  const search = document.getElementById('filterSearch').value.toLowerCase();
  const role = document.getElementById('filterRole').value;
  const sentiment = document.getElementById('filterSentiment').value;
  const lang = document.getElementById('filterLang').value;
  const task = document.getElementById('filterTask').value;
  const rows = document.querySelectorAll('#commentTableBody tr');
  let count = 0;
  rows.forEach(row => {{
    const rName = row.dataset.name || '';
    const rRole = row.dataset.role || '';
    const rSentiment = row.dataset.sentiment || '';
    const rLang = row.dataset.lang || '';
    const rTask = row.dataset.task || '';
    const rBranch = row.dataset.branch || '';
    const rComment = row.dataset.comment || '';
    let show = true;
    if (search && !rName.includes(search) && !rBranch.includes(search) && !rComment.includes(search)) show = false;
    if (role && rRole !== role) show = false;
    if (sentiment && rSentiment !== sentiment) show = false;
    if (lang && rLang !== lang) show = false;
    if (task && rTask !== task) show = false;
    row.style.display = show ? '' : 'none';
    if (show) count++;
  }});
  document.getElementById('filteredCount').textContent = count + ' shown';
}}

// Table Sort
let sortCol = -1, sortAsc = true;
function sortTable(col) {{
  if (sortCol === col) sortAsc = !sortAsc;
  else {{ sortCol = col; sortAsc = true; }}
  const tbody = document.getElementById('commentTableBody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  rows.sort((a, b) => {{
    let va = a.cells[col].textContent.trim();
    let vb = b.cells[col].textContent.trim();
    const na = parseFloat(va.replace('%',''));
    const nb = parseFloat(vb.replace('%',''));
    if (!isNaN(na) && !isNaN(nb)) {{ va = na; vb = nb; }}
    else {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
    if (va < vb) return sortAsc ? -1 : 1;
    if (va > vb) return sortAsc ? 1 : -1;
    return 0;
  }});
  rows.forEach(r => tbody.appendChild(r));
}}

// Init count
applyFilters();
</script>
</div>
</body>
</html>
"""

OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_HTML.write_text(html, encoding='utf-8')
print(f"Dashboard written to {OUTPUT_HTML} ({len(html)//1024}KB)")
print(f"  {total_comments} comments, {len(english_comments)} English, {len(marathi_comments)} Marathi")
print(f"  Overall: {len(positive)} positive, {len(neutral)} neutral, {len(negative)} negative")
print(f"  English: {len(en_positive)} pos, {len(en_neutral)} neu, {len(en_negative)} neg")
print(f"  Marathi: {len(mr_positive)} pos, {len(mr_neutral)} neu, {len(mr_negative)} neg")
