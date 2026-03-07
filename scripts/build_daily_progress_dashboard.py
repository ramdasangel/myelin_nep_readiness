#!/usr/bin/env python3
"""Build the full Micro-Intervention Daily Progress Dashboard HTML."""
import csv
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TASK_MAPPING_CSV = BASE / "output" / "micro_intervention_report.csv"
DAILY_PROGRESS_CSV = BASE / "assets" / "myelin_stat_ro" / "daily_progress_full.csv"
OUTPUT_HTML = BASE / "output" / "daily_progress_dashboard.html"

# ── Task metadata ──
TASK_META = {
    'T01': {'label': 'Notice One Learner', 'fp': 'FP-1', 'depth': 'D1→D2', 'cat': 'entry'},
    'T02': {'label': 'One Adjustment', 'fp': 'FP-1', 'depth': 'D2→D3', 'cat': 'growth'},
    'T03': {'label': 'Change One Example', 'fp': 'FP-2', 'depth': 'D1→D2', 'cat': 'entry'},
    'T04': {'label': 'Ask a Why/How', 'fp': 'FP-2', 'depth': 'D2→D3', 'cat': 'growth'},
    'T05': {'label': 'End-of-Class Reflection', 'fp': 'FP-3', 'depth': 'D1→D2', 'cat': 'entry'},
    'T06': {'label': 'Try One Small Change', 'fp': 'FP-3', 'depth': 'D2→D3', 'cat': 'growth'},
    'T07': {'label': 'Quick Check', 'fp': 'FP-4', 'depth': 'D1→D2', 'cat': 'entry'},
    'T08': {'label': 'Spot One Pattern', 'fp': 'FP-4', 'depth': 'D2→D3', 'cat': 'growth'},
    'T09': {'label': 'Teacher Touchpoint', 'fp': 'FP-5', 'depth': 'D1→D2', 'cat': 'entry'},
    'T10': {'label': 'Parent Signal', 'fp': 'FP-5', 'depth': 'D1→D2', 'cat': 'entry'},
    'T11': {'label': 'Student Voice', 'fp': 'FP-1', 'depth': 'Cross-FP', 'cat': 'cross'},
    'T12': {'label': 'Pause & Name', 'fp': 'FP-4', 'depth': 'Cross-FP', 'cat': 'cross'},
}

# TaskId (MongoDB ObjectId) → TaskCode mapping (both series)
TASKID_TO_CODE = {
    # Original series
    '697b1e2cc01f188423ea7e0f': 'T01', '697b1e2cc01f188423ea7e10': 'T02',
    '697b1e2cc01f188423ea7e11': 'T03', '697b1e2cc01f188423ea7e12': 'T04',
    '697b1e2cc01f188423ea7e13': 'T05', '697b1e2cc01f188423ea7e14': 'T06',
    '697b1e2cc01f188423ea7e15': 'T07', '697b1e2cc01f188423ea7e16': 'T08',
    '697b1e2cc01f188423ea7e17': 'T09', '697b1e2cc01f188423ea7e18': 'T10',
    '697b1e2cc01f188423ea7e19': 'T11', '697b1e2cc01f188423ea7e1a': 'T12',
    # Duplicate series
    '697b1e3bc671c89acb64125a': 'T01', '697b1e3bc671c89acb64125b': 'T02',
    '697b1e3bc671c89acb64125c': 'T03', '697b1e3bc671c89acb64125d': 'T04',
    '697b1e3bc671c89acb64125e': 'T05', '697b1e3bc671c89acb64125f': 'T06',
    '697b1e3bc671c89acb641260': 'T07', '697b1e3bc671c89acb641261': 'T08',
    '697b1e3bc671c89acb641262': 'T09', '697b1e3bc671c89acb641263': 'T10',
    '697b1e3bc671c89acb641264': 'T11', '697b1e3bc671c89acb641265': 'T12',
}

# Mapping dates from prod
MAPPING_DATES = {
    '696ddd09c6f1e9689723f2b4': '2026-02-03', '696dc548c6f1e9689723af89': '2026-02-03',
    '697219bfab8e501024780612': '2026-02-03', '696ddcde7c028268c457db57': '2026-02-03',
    '696ddc927c028268c457d8b1': '2026-02-03', '6972199d5dab9a102eb39826': '2026-02-03',
    '6971e5305dab9a102eb1f2c8': '2026-02-03', '697219805dab9a102eb396b0': '2026-02-03',
    '696ddc99c6f1e9689723ef31': '2026-02-03', '6981c4096e1ccd12c7ec0233': '2026-02-03',
    '6971a29002a54777460225f2': '2026-02-03', '6971fb745dab9a102eb2b1ad': '2026-02-03',
    '6971a89d02a54777460240a8': '2026-02-03', '6971fb855dab9a102eb2b271': '2026-02-03',
    '6971dfe3ab8e501024764488': '2026-02-03', '696ddca8c6f1e9689723efd3': '2026-02-03',
    '6971e7fbab8e501024767b33': '2026-02-03', '696ddc94c6f1e9689723ef15': '2026-02-03',
    '69720fde5dab9a102eb3410a': '2026-02-03', '69722246ab8e5010247858cb': '2026-02-04',
    '697214f35dab9a102eb374e1': '2026-02-04', '69720d715dab9a102eb33146': '2026-02-04',
    '69720be1ab8e501024778e90': '2026-02-04', '69720f3a5dab9a102eb33e6b': '2026-02-04',
    '69724f1eab8e50102479e59a': '2026-02-04', '6971d0e7ab8e50102475973d': '2026-02-04',
    '696ddd4bc6f1e9689723f464': '2026-02-04', '696ddd357c028268c457dec0': '2026-02-04',
    '696ddc8e7c028268c457d8a1': '2026-02-04', '6971b04002a5477746025f87': '2026-02-04',
    '696ddc92c6f1e9689723eefc': '2026-02-04', '6971d3685dab9a102eb141f3': '2026-02-04',
    '6971d6885dab9a102eb17b8e': '2026-02-04', '6971b04c02a5477746026007': '2026-02-04',
    '6971fe145dab9a102eb2bfa5': '2026-02-04', '6971ec745dab9a102eb23576': '2026-02-04',
    '69708fd34f32384a3ca50f55': '2026-02-04', '697ae9896864ae3d4877bd71': '2026-02-04',
    '6971d23aab8e50102475a42c': '2026-02-04', '6971fd77ab8e501024772b23': '2026-02-04',
    '6971ff025dab9a102eb2c7ca': '2026-02-04', '6971af9002a5477746025c55': '2026-02-04',
    '69709080f0a6d02140822d2c': '2026-02-04', '697225665dab9a102eb40bca': '2026-02-04',
    '6971dadc5dab9a102eb1af24': '2026-02-04', '6971e23cab8e501024765410': '2026-02-04',
    '69724cdb5dab9a102eb56a2a': '2026-02-04', '697090804f32384a3ca51136': '2026-02-04',
    '6971f59b5dab9a102eb28083': '2026-02-04', '6971d3d2ab8e50102475bb7a': '2026-02-04',
    '6971b08d02a5477746026172': '2026-02-04', '6971a77c2edad4557d61a602': '2026-02-04',
    '69722b94ab8e501024789e49': '2026-02-04', '696de1e7c6f1e96897241a2a': '2026-02-04',
    '696ddce5c6f1e9689723f17f': '2026-02-04', '6971b6669f16fa0f9d680cf8': '2026-02-04',
    '69720006ab8e501024773922': '2026-02-04', '6971fe42ab8e501024772ff7': '2026-02-04',
    '6971b2dd2edad4557d61dca1': '2026-02-04', '6971b05d02a5477746026095': '2026-02-04',
    '697217a15dab9a102eb385da': '2026-02-04', '6971fc335dab9a102eb2b4af': '2026-02-04',
    '697246965dab9a102eb53bb3': '2026-02-04', '697077fdf0a6d0214081c2e8': '2026-02-04',
    '6971db1d5dab9a102eb1b111': '2026-02-04', '6971d8caab8e501024760818': '2026-02-04',
    '6971da255dab9a102eb1a78d': '2026-02-04', '69719f6602a5477746021c42': '2026-02-04',
    '6971db5c5dab9a102eb1b3cc': '2026-02-04', '6971d94fab8e501024760d47': '2026-02-04',
    '6971d992ab8e50102476110d': '2026-02-04', '6971d97dab8e501024760f79': '2026-02-04',
    '6971d8ed5dab9a102eb198fa': '2026-02-04', '6971af8b2edad4557d61c5fc': '2026-02-04',
    '6971eff35dab9a102eb25ca8': '2026-02-04', '697217e35dab9a102eb389b4': '2026-02-04',
    '696ddc857c028268c457d889': '2026-02-04', '6972077a5dab9a102eb3014c': '2026-02-04',
    '6972077a5dab9a102eb3013d': '2026-02-04', '697254c6ab8e5010247a085f': '2026-02-04',
    '69723b99ab8e501024795d31': '2026-02-04', '696ddca77c028268c457d966': '2026-02-04',
    '696ddc6ac6f1e9689723ee6e': '2026-02-04', '696ddd557c028268c457df57': '2026-02-04',
    '69721109ab8e50102477b58d': '2026-02-05', '696ddd877c028268c457e150': '2026-02-05',
    '6971d5feab8e50102475e247': '2026-02-05', '696df9147c028268c4584268': '2026-02-05',
    '6971da395dab9a102eb1a89b': '2026-02-05', '6971d4f4ab8e50102475d357': '2026-02-05',
    '6971d76c5dab9a102eb18864': '2026-02-05', '6971d0f7ab8e501024759815': '2026-02-05',
    '696ddd1b7c028268c457dde3': '2026-02-05', '697238315dab9a102eb4c831': '2026-02-05',
    '6971e9865dab9a102eb21802': '2026-02-05', '6971b9aa9f16fa0f9d681db9': '2026-02-05',
    '69721d755dab9a102eb3bf29': '2026-02-05', '6969d7f9217639055d24ea97': '2026-02-05',
    '6971dcd9ab8e50102476316c': '2026-02-05', '696ddcc07c028268c457da95': '2026-02-05',
    '696ddcab7c028268c457d9a6': '2026-02-05', '6971d076ab8e5010247591cb': '2026-02-05',
    '6971d15eab8e501024759af5': '2026-02-05', '696ddcaec6f1e9689723f019': '2026-02-05',
    '6971e15d5dab9a102eb1da4d': '2026-02-05', '6971c2bfdc25d2246ca2c3e8': '2026-02-05',
    '696ddd397c028268c457dec8': '2026-02-05', '6971d0775dab9a102eb1210a': '2026-02-05',
    '696ddd3bc6f1e9689723f3c3': '2026-02-05', '6971f954ab8e501024770b3b': '2026-02-05',
    '697210925dab9a102eb34729': '2026-02-05', '697210c6ab8e50102477b348': '2026-02-05',
    '6971d9565dab9a102eb19d4d': '2026-02-05', '69722dc0ab8e50102478ab1b': '2026-02-05',
    '697201485dab9a102eb2d4cb': '2026-02-05', '6971d05eab8e50102475918e': '2026-02-06',
    '6972379bab8e501024793a54': '2026-02-06', '6971da49ab8e501024761821': '2026-02-06',
    '6971d569ab8e50102475d9fe': '2026-02-06', '69722d54ab8e50102478a8e7': '2026-02-07',
    '697236de5dab9a102eb4b9a4': '2026-02-07', '69723c365dab9a102eb4e733': '2026-02-07',
    '6971fe985dab9a102eb2c57c': '2026-02-07',
    # Added 2026-02-23
    '696ddcad7c028268c457d9ae': '2026-02-05', '696ddd40c6f1e9689723f40f': '2026-02-17',
    '696ddeabc6f1e96897240033': '2026-02-11', '696ddf1bc6f1e968972403d7': '2026-02-11',
    '697191a02edad4557d6157e2': '2026-02-11', '69719f4102a5477746021be2': '2026-02-11',
    '6971a5e202a54777460232a6': '2026-02-11', '6971a5ff02a5477746023303': '2026-02-11',
    '6971a68f02a5477746023591': '2026-02-11', '6971ad702edad4557d61bf7c': '2026-02-11',
    '6971ad7302a547774602557e': '2026-02-11', '6971ad732edad4557d61bf88': '2026-02-11',
    '6971af4a02a5477746025bd6': '2026-02-11', '6971af8a02a5477746025c41': '2026-02-10',
    '6971af8d02a5477746025c49': '2026-02-11', '6971af932edad4557d61c628': '2026-02-11',
    '6971b1ed02a5477746026b83': '2026-02-11', '6971b4952edad4557d61eb25': '2026-02-11',
    '6971b5c49f16fa0f9d680a84': '2026-02-11', '6971b5e69f16fa0f9d680b03': '2026-02-11',
    '6971b70302a5477746028d63': '2026-02-11', '6971b9af9f16fa0f9d681dc5': '2026-02-11',
    '6971d374ab8e50102475b55d': '2026-02-09', '6971d643ab8e50102475e619': '2026-02-11',
    '6971d68b5dab9a102eb17bb7': '2026-02-11', '6971d89fab8e50102476053e': '2026-02-11',
    '6971e039ab8e5010247646cf': '2026-02-09', '6971eca3ab8e50102476abee': '2026-02-10',
    '69721950ab8e50102478015d': '2026-02-09', '69721971ab8e501024780326': '2026-02-09',
    '6972197dab8e501024780396': '2026-02-09', '69721984ab8e5010247803d0': '2026-02-09',
    '697219865dab9a102eb396ed': '2026-02-09', '69721988ab8e5010247803f0': '2026-02-09',
    '69721bb6ab8e501024781a5e': '2026-02-09', '69722cea5dab9a102eb43aa9': '2026-02-10',
    '69723a285dab9a102eb4dba1': '2026-02-11', '69723c1cab8e501024796146': '2026-02-09',
    '69723d2a5dab9a102eb4f012': '2026-02-11', '69723ee8ab8e5010247975fe': '2026-02-11',
    '69723fe3ab8e501024797c8e': '2026-02-11', '69724568ab8e50102479a232': '2026-02-09',
    '697248935dab9a102eb547de': '2026-02-11', '697255945dab9a102eb59def': '2026-02-09',
    '697c3a0c5b12565c25b3e8df': '2026-02-09', '697c5b4b13f4105c6faa491e': '2026-02-09',
}

# ── Step 1: Read task mapping data (DES only) ──
users = {}
with open(TASK_MAPPING_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        school = row['SchoolName'].strip()
        if school != 'Deccan Education Society':
            continue
        uid = row['UserId'].strip()
        task_list_raw = row['TaskList'].strip()
        task_codes = [t.split('-')[0].strip() for t in task_list_raw.split(' | ') if t.strip().startswith('T')]
        users[uid] = {
            'firstName': row['FirstName'].strip(),
            'lastName': row['LastName'].strip(),
            'role': row['Role'].strip(),
            'schoolName': school,
            'branchName': row['BranchName'].strip(),
            'branchCode': row['BranchCode'].strip(),
            'tasksMapped': task_codes,
            'tasksMappedCount': len(task_codes),
            'mappingDate': MAPPING_DATES.get(uid, ''),
            # daily progress aggregates
            'daysLogged': set(),
            'totalChecked': 0,
            'totalUnchecked': 0,
            'totalComments': 0,
            'taskLogs': defaultdict(lambda: {'checked': 0, 'unchecked': 0, 'comments': 0}),
            'dailyDetail': [],  # list of {date, taskCode, isChecked, hasComment}
        }

# ── Step 2: Read daily progress ──
des_uids = set(users.keys())
with open(DAILY_PROGRESS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        uid = row['userId'].strip()
        if uid not in des_uids:
            continue
        task_id = row['taskId'].strip()
        task_code = TASKID_TO_CODE.get(task_id, '')
        if not task_code:
            continue
        submit_date = row['submitDate'].strip()
        is_checked = row['isChecked'].strip() == 'true'
        has_comment = row['hasComment'].strip() == 'true'

        u = users[uid]
        u['daysLogged'].add(submit_date)
        if is_checked:
            u['totalChecked'] += 1
        else:
            u['totalUnchecked'] += 1
        if has_comment:
            u['totalComments'] += 1
        tl = u['taskLogs'][task_code]
        if is_checked:
            tl['checked'] += 1
        else:
            tl['unchecked'] += 1
        if has_comment:
            tl['comments'] += 1
        u['dailyDetail'].append({
            'date': submit_date, 'task': task_code,
            'checked': is_checked, 'comment': has_comment
        })

# ── Step 3: Compute per-user metrics ──
user_list = []
for uid, u in users.items():
    days_logged = len(u['daysLogged'])
    total_task_logs = u['totalChecked'] + u['totalUnchecked']
    completion_rate = round(u['totalChecked'] / total_task_logs * 100, 1) if total_task_logs > 0 else 0
    comment_rate = round(u['totalComments'] / total_task_logs * 100, 1) if total_task_logs > 0 else 0

    # Consistency: days logged / days since mapping (capped at 21)
    # If mappingDate is missing, infer as one day before first log date
    from datetime import date, timedelta
    mapping_dt = u['mappingDate']
    if not mapping_dt and days_logged > 0:
        first_log = min(u['daysLogged'])
        mapping_dt = (date.fromisoformat(first_log) - timedelta(days=1)).isoformat()
        u['mappingDate'] = mapping_dt  # update for display too

    if mapping_dt and days_logged > 0:
        mapped = date.fromisoformat(mapping_dt)
        today = date(2026, 3, 2)
        days_available = min((today - mapped).days, 21)
        consistency = round(days_logged / days_available * 100, 1) if days_available > 0 else 0
    else:
        days_available = 0
        consistency = 0

    # FP coverage from mapped tasks
    fps = sorted(set(TASK_META[tc]['fp'] for tc in u['tasksMapped'] if tc in TASK_META))
    depths = sorted(set(TASK_META[tc]['depth'] for tc in u['tasksMapped'] if tc in TASK_META))

    # Per-task log summary
    task_log_summary = {}
    for tc in u['tasksMapped']:
        tl = u['taskLogs'].get(tc, {'checked': 0, 'unchecked': 0, 'comments': 0})
        task_log_summary[tc] = tl

    user_list.append({
        'uid': uid,
        'name': f"{u['firstName']} {u['lastName']}".strip(),
        'role': u['role'] or '—',
        'school': u['schoolName'],
        'branch': u['branchName'],
        'branchCode': u['branchCode'],
        'mappingDate': u['mappingDate'],
        'tasksMapped': u['tasksMapped'],
        'tasksMappedCount': u['tasksMappedCount'],
        'fps': fps,
        'depths': depths,
        'daysLogged': days_logged,
        'daysAvailable': days_available,
        'totalChecked': u['totalChecked'],
        'totalUnchecked': u['totalUnchecked'],
        'totalLogs': total_task_logs,
        'totalComments': u['totalComments'],
        'completionRate': completion_rate,
        'commentRate': comment_rate,
        'consistency': consistency,
        'taskLogSummary': task_log_summary,
    })

# Sort by consistency desc
user_list.sort(key=lambda x: (-x['consistency'], -x['daysLogged'], x['name']))

# ── Step 4: Aggregate stats ──
total_users = len(user_list)
active_users = sum(1 for u in user_list if u['daysLogged'] > 0)
zero_log_users = total_users - active_users
avg_tasks = round(sum(u['tasksMappedCount'] for u in user_list) / total_users, 1)
avg_days = round(sum(u['daysLogged'] for u in user_list) / total_users, 1)
avg_days_active = round(sum(u['daysLogged'] for u in user_list if u['daysLogged'] > 0) / max(active_users, 1), 1)
total_checked = sum(u['totalChecked'] for u in user_list)
total_unchecked = sum(u['totalUnchecked'] for u in user_list)
total_comments = sum(u['totalComments'] for u in user_list)
total_log_entries = total_checked + total_unchecked
global_completion = round(total_checked / total_log_entries * 100, 1) if total_log_entries > 0 else 0
global_comment_rate = round(total_comments / total_log_entries * 100, 1) if total_log_entries > 0 else 0
teachers = sum(1 for u in user_list if u['role'] == 'Teacher')
leaders = sum(1 for u in user_list if u['role'] == 'Leader')
avg_consistency_active = round(sum(u['consistency'] for u in user_list if u['consistency'] > 0) / max(sum(1 for u in user_list if u['consistency'] > 0), 1), 1)

# ── Aggregates for charts ──
# Task-level completion rates
task_completion = {}
for tc in sorted(TASK_META.keys()):
    ch = sum(u['taskLogSummary'].get(tc, {}).get('checked', 0) for u in user_list)
    uch = sum(u['taskLogSummary'].get(tc, {}).get('unchecked', 0) for u in user_list)
    total = ch + uch
    task_completion[tc] = {'checked': ch, 'unchecked': uch, 'rate': round(ch/total*100, 1) if total > 0 else 0, 'adopters': sum(1 for u in user_list if tc in u['tasksMapped'])}

# FP-level: mapped count vs logged count
fp_stats = {}
for fp in ['FP-1', 'FP-2', 'FP-3', 'FP-4', 'FP-5']:
    fp_tasks = [tc for tc, m in TASK_META.items() if m['fp'] == fp]
    mapped = sum(sum(1 for tc in u['tasksMapped'] if tc in fp_tasks) for u in user_list)
    logged_ch = sum(sum(u['taskLogSummary'].get(tc, {}).get('checked', 0) for tc in fp_tasks) for u in user_list)
    logged_uch = sum(sum(u['taskLogSummary'].get(tc, {}).get('unchecked', 0) for tc in fp_tasks) for u in user_list)
    fp_stats[fp] = {'mapped': mapped, 'checked': logged_ch, 'unchecked': logged_uch}

# Depth-level
depth_stats = {}
for cat_label, cat_key in [('D1→D2 (Entry)', 'entry'), ('D2→D3 (Growth)', 'growth'), ('Cross-FP', 'cross')]:
    cat_tasks = [tc for tc, m in TASK_META.items() if m['cat'] == cat_key]
    mapped = sum(sum(1 for tc in u['tasksMapped'] if tc in cat_tasks) for u in user_list)
    logged_ch = sum(sum(u['taskLogSummary'].get(tc, {}).get('checked', 0) for tc in cat_tasks) for u in user_list)
    logged_uch = sum(sum(u['taskLogSummary'].get(tc, {}).get('unchecked', 0) for tc in cat_tasks) for u in user_list)
    depth_stats[cat_label] = {'mapped': mapped, 'checked': logged_ch, 'unchecked': logged_uch}

# Scatter data: tasks mapped vs days logged
scatter_data = [{'x': u['tasksMappedCount'], 'y': u['daysLogged'], 'name': u['name'], 'role': u['role']} for u in user_list]

# Consistency distribution
consistency_buckets = defaultdict(int)
for u in user_list:
    if u['consistency'] == 0:
        consistency_buckets['0%'] += 1
    elif u['consistency'] <= 10:
        consistency_buckets['1-10%'] += 1
    elif u['consistency'] <= 20:
        consistency_buckets['11-20%'] += 1
    elif u['consistency'] <= 30:
        consistency_buckets['21-30%'] += 1
    elif u['consistency'] <= 50:
        consistency_buckets['31-50%'] += 1
    else:
        consistency_buckets['>50%'] += 1

consistency_order = ['0%', '1-10%', '11-20%', '21-30%', '31-50%', '>50%']
consistency_values = [consistency_buckets.get(k, 0) for k in consistency_order]

# Daily activity timeline
daily_activity = defaultdict(lambda: {'checked': 0, 'unchecked': 0, 'users': set()})
for u in user_list:
    for d in u.get('taskLogSummary', {}).values():
        pass
# Re-read raw for daily timeline
with open(DAILY_PROGRESS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        uid = row['userId'].strip()
        if uid not in des_uids:
            continue
        submit_date = row['submitDate'].strip()
        is_checked = row['isChecked'].strip() == 'true'
        da = daily_activity[submit_date]
        if is_checked:
            da['checked'] += 1
        else:
            da['unchecked'] += 1
        da['users'].add(uid)

daily_dates = sorted(daily_activity.keys())
daily_checked = [daily_activity[d]['checked'] for d in daily_dates]
daily_unchecked = [daily_activity[d]['unchecked'] for d in daily_dates]
daily_active_users = [len(daily_activity[d]['users']) for d in daily_dates]

# Day names for timeline labels
DAY_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
daily_labels = []
for d in daily_dates:
    dt = date.fromisoformat(d)
    day_name = DAY_ABBR[dt.weekday()]
    daily_labels.append(f"{d.replace('2026-','')} {day_name}")

# Role comparison
role_stats = {}
for role in ['Teacher', 'Leader']:
    ru = [u for u in user_list if u['role'] == role]
    if ru:
        role_stats[role] = {
            'count': len(ru),
            'avgDays': round(sum(u['daysLogged'] for u in ru) / len(ru), 1),
            'avgConsistency': round(sum(u['consistency'] for u in ru) / len(ru), 1),
            'avgCompletion': round(sum(u['completionRate'] for u in ru if u['totalLogs'] > 0) / max(sum(1 for u in ru if u['totalLogs'] > 0), 1), 1),
        }

# Mapped vs Logged per FP (for grouped bar)
fp_mapped_vs_logged = {fp: {'mapped_users': 0, 'logged_users': 0} for fp in ['FP-1','FP-2','FP-3','FP-4','FP-5']}
for u in user_list:
    for fp in ['FP-1','FP-2','FP-3','FP-4','FP-5']:
        fp_tasks = [tc for tc, m in TASK_META.items() if m['fp'] == fp]
        if any(tc in u['tasksMapped'] for tc in fp_tasks):
            fp_mapped_vs_logged[fp]['mapped_users'] += 1
        if any(u['taskLogSummary'].get(tc, {}).get('checked', 0) > 0 for tc in fp_tasks):
            fp_mapped_vs_logged[fp]['logged_users'] += 1

# ── Build HTML ──
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage 5 — Micro-Intervention Daily Progress Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {{
  --primary: #1a365d; --accent: #2b6cb0; --green: #38a169; --amber: #d69e2e;
  --orange: #ed8936; --red: #e53e3e; --bg: #f7fafc; --card: #ffffff;
  --border: #e2e8f0; --text: #2d3748; --muted: #718096; --light: #ebf4ff;
  --fp1: #6366f1; --fp2: #ec4899; --fp3: #f59e0b; --fp4: #10b981; --fp5: #3b82f6;
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
.fp-tag {{ display: inline-block; padding: 2px 6px; border-radius: 10px; font-size: 9px; font-weight: 700; margin: 1px; white-space: nowrap; }}
.fp-tag.fp1 {{ background: #eef2ff; color: var(--fp1); }} .fp-tag.fp2 {{ background: #fdf2f8; color: var(--fp2); }}
.fp-tag.fp3 {{ background: #fffbeb; color: var(--fp3); }} .fp-tag.fp4 {{ background: #ecfdf5; color: var(--fp4); }}
.fp-tag.fp5 {{ background: #eff6ff; color: var(--fp5); }}
.bar-inline {{ display: inline-block; height: 12px; border-radius: 3px; }}
.bar-green {{ background: var(--green); }} .bar-red {{ background: #feb2b2; }} .bar-gray {{ background: var(--border); }}
.consistency-badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 10px; font-weight: 700; }}
.cons-high {{ background: #f0fff4; color: var(--green); }} .cons-med {{ background: #fffbeb; color: var(--amber); }}
.cons-low {{ background: #fff5f5; color: var(--red); }} .cons-zero {{ background: #f1f5f9; color: var(--muted); }}
.role-compare {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
.role-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.role-card h4 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
.role-card .metric {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 13px; }}
.role-card .metric .val {{ font-weight: 700; }}
@media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} .role-compare {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>Stage 5 — Micro-Intervention Daily Progress Dashboard</h1>
  <p>Tasks → Mapping → Daily Logs &nbsp;|&nbsp; Deccan Education Society &nbsp;|&nbsp; {total_users} Users &nbsp;|&nbsp; {total_log_entries} Task-Log Entries &nbsp;|&nbsp; Data through 2026-03-02</p>
</div>
<div class="container">

<!-- KPI Row -->
<div class="kpi-row">
  <div class="kpi"><div class="value">{total_users}</div><div class="label">Total Users</div></div>
  <div class="kpi green"><div class="value">{active_users}</div><div class="label">Active (≥1 Log)</div></div>
  <div class="kpi red"><div class="value">{zero_log_users}</div><div class="label">Zero Logs</div></div>
  <div class="kpi amber"><div class="value">{avg_days_active}</div><div class="label">Avg Days (Active)</div></div>
  <div class="kpi green"><div class="value">{global_completion}%</div><div class="label">Completion Rate</div></div>
  <div class="kpi"><div class="value">{global_comment_rate}%</div><div class="label">Comment Rate</div></div>
  <div class="kpi orange"><div class="value">{avg_consistency_active}%</div><div class="label">Avg Consistency</div></div>
  <div class="kpi"><div class="value">{total_log_entries}</div><div class="label">Total Log Entries</div></div>
</div>

<!-- Role Comparison -->
<div class="section-title">Role Comparison — Teacher vs Leader</div>
<div class="role-compare">
"""
for role_name in ['Teacher', 'Leader']:
    rs = role_stats.get(role_name, {'count': 0, 'avgDays': 0, 'avgConsistency': 0, 'avgCompletion': 0})
    html += f"""<div class="role-card"><h4>{role_name}s ({rs['count']})</h4>
  <div class="metric"><span>Avg Days Logged</span><span class="val">{rs['avgDays']}</span></div>
  <div class="metric"><span>Avg Consistency</span><span class="val">{rs['avgConsistency']}%</span></div>
  <div class="metric"><span>Avg Completion Rate</span><span class="val">{rs['avgCompletion']}%</span></div>
</div>"""

html += """</div>

<div class="section-title">Charts — Activity, Completion &amp; Correlation</div>
"""

# Chart canvases
html += """
<div class="chart-grid">
  <div class="chart-box full"><h3>Daily Activity Timeline — Checked vs Unchecked + Active Users</h3><canvas id="chartDailyActivity"></canvas></div>
</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Task Completion Rate by Task (T01–T12)</h3><canvas id="chartTaskCompletion"></canvas></div>
  <div class="chart-box"><h3>FP: Mapped Users vs Users Who Logged (Checked ≥1)</h3><canvas id="chartFPMappedLogged"></canvas></div>
</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Depth Intent: Selections vs Checked Logs</h3><canvas id="chartDepthMappedLogged"></canvas></div>
  <div class="chart-box"><h3>Consistency Distribution (Active Users)</h3><canvas id="chartConsistency"></canvas></div>
</div>
<div class="chart-grid">
  <div class="chart-box"><h3>Correlation: Tasks Mapped vs Days Logged</h3><canvas id="chartScatter"></canvas></div>
  <div class="chart-box"><h3>Completion Rate by FP</h3><canvas id="chartFPCompletion"></canvas></div>
</div>
"""

# Filter bar
html += """
<div class="section-title">User Detail Table</div>
<div class="filter-bar">
  <label>Filter:</label>
  <input type="text" id="filterSearch" placeholder="Search name, school, branch..." oninput="applyFilters()">
  <select id="filterRole" onchange="applyFilters()"><option value="">All Roles</option><option value="Teacher">Teacher</option><option value="Leader">Leader</option></select>
  <select id="filterActivity" onchange="applyFilters()"><option value="">All</option><option value="active">Active (≥1 log)</option><option value="zero">Zero Logs</option></select>
  <span class="count-badge" id="filteredCount"></span>
</div>
"""

# Table
html += """
<div class="table-section">
<table class="data" id="userTable">
<thead><tr>
  <th onclick="sortTable(0)">#</th>
  <th onclick="sortTable(1)">Name</th>
  <th onclick="sortTable(2)">Role</th>
  <th onclick="sortTable(3)">School / Branch</th>
  <th onclick="sortTable(4)">Mapped</th>
  <th onclick="sortTable(5)">FP</th>
  <th onclick="sortTable(6)">Depth</th>
  <th onclick="sortTable(7)">Mapped On</th>
  <th onclick="sortTable(8)">Days</th>
  <th onclick="sortTable(9)">Checked</th>
  <th onclick="sortTable(10)">Unchecked</th>
  <th onclick="sortTable(11)">Comments</th>
  <th onclick="sortTable(12)">Completion%</th>
  <th onclick="sortTable(13)">Consistency%</th>
  <th>Mapped→Logged</th>
</tr></thead>
<tbody id="userTableBody">
"""

for i, u in enumerate(user_list):
    fp_tags = ''.join(f'<span class="fp-tag fp{fp[-1]}">{fp}</span>' for fp in u['fps'])
    depth_tags = ''.join(f'<span class="fp-tag" style="background:#f1f5f9;color:#475569">{d}</span>' for d in u['depths'])

    # Consistency badge
    c = u['consistency']
    if c == 0: cons_cls = 'cons-zero'
    elif c < 15: cons_cls = 'cons-low'
    elif c < 35: cons_cls = 'cons-med'
    else: cons_cls = 'cons-high'

    # Mapped→Logged mini bar per task
    task_bars = []
    for tc in sorted(u['tasksMapped']):
        tl = u['taskLogSummary'].get(tc, {'checked': 0, 'unchecked': 0})
        ch = tl.get('checked', 0)
        uch = tl.get('unchecked', 0)
        total = ch + uch
        if total == 0:
            task_bars.append(f'<span style="font-size:9px;color:var(--muted)">{tc}:0</span>')
        else:
            task_bars.append(f'<span style="font-size:9px">{tc}:<b style="color:var(--green)">{ch}</b>/{total}</span>')

    branch_display = u['branch']
    if u['branchCode']:
        branch_display += f" ({u['branchCode']})"

    html += f"""<tr data-name="{u['name'].lower()}" data-role="{u['role']}" data-branch="{u['branch'].lower()}" data-days="{u['daysLogged']}">
  <td>{i+1}</td>
  <td><b>{u['name']}</b></td>
  <td>{u['role']}</td>
  <td style="max-width:220px;font-size:10px">{branch_display}</td>
  <td style="text-align:center"><b>{u['tasksMappedCount']}</b></td>
  <td>{fp_tags}</td>
  <td>{depth_tags}</td>
  <td style="white-space:nowrap;font-size:10px">{u['mappingDate'].replace('2026-','') if u['mappingDate'] else '—'}</td>
  <td style="text-align:center"><b>{u['daysLogged']}</b></td>
  <td style="text-align:center;color:var(--green)">{u['totalChecked']}</td>
  <td style="text-align:center;color:var(--red)">{u['totalUnchecked']}</td>
  <td style="text-align:center">{u['totalComments']}</td>
  <td style="text-align:center"><b>{u['completionRate']}%</b></td>
  <td style="text-align:center"><span class="consistency-badge {cons_cls}">{u['consistency']}%</span></td>
  <td style="font-size:9px">{' '.join(task_bars)}</td>
</tr>"""

html += "</tbody></table></div>"

# ── JavaScript for Charts & Interactivity ──
html += f"""
<script>
// Daily Activity Timeline
new Chart(document.getElementById('chartDailyActivity'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(daily_labels)},
    datasets: [
      {{ label: 'Checked', data: {json.dumps(daily_checked)}, backgroundColor: '#38a169', borderRadius: 3, order: 2 }},
      {{ label: 'Unchecked', data: {json.dumps(daily_unchecked)}, backgroundColor: '#feb2b2', borderRadius: 3, order: 3 }},
      {{ label: 'Active Users', data: {json.dumps(daily_active_users)}, type: 'line', borderColor: '#2b6cb0', pointBackgroundColor: '#2b6cb0', borderWidth: 2, tension: 0.3, yAxisID: 'y1', order: 1 }}
    ]
  }},
  options: {{
    responsive: true, plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ stacked: true, title: {{ display: true, text: 'Submit Date (Feb 2026)' }} }},
      y: {{ stacked: true, title: {{ display: true, text: 'Task Entries' }}, beginAtZero: true }},
      y1: {{ position: 'right', title: {{ display: true, text: 'Active Users' }}, beginAtZero: true, grid: {{ drawOnChartArea: false }} }}
    }}
  }}
}});

// Task Completion Rate
new Chart(document.getElementById('chartTaskCompletion'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([f"{tc} {TASK_META[tc]['label']}" for tc in sorted(TASK_META.keys())])},
    datasets: [
      {{ label: 'Completion %', data: {json.dumps([task_completion[tc]['rate'] for tc in sorted(TASK_META.keys())])},
        backgroundColor: {json.dumps([{'FP-1':'#6366f1','FP-2':'#ec4899','FP-3':'#f59e0b','FP-4':'#10b981','FP-5':'#3b82f6'}[TASK_META[tc]['fp']] for tc in sorted(TASK_META.keys())])}, borderRadius: 4 }}
    ]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ max: 100, title: {{ display: true, text: 'Completion %' }} }} }} }}
}});

// FP Mapped vs Logged
new Chart(document.getElementById('chartFPMappedLogged'), {{
  type: 'bar',
  data: {{
    labels: ['FP-1','FP-2','FP-3','FP-4','FP-5'],
    datasets: [
      {{ label: 'Users Mapped', data: {json.dumps([fp_mapped_vs_logged[fp]['mapped_users'] for fp in ['FP-1','FP-2','FP-3','FP-4','FP-5']])}, backgroundColor: '#93c5fd', borderRadius: 4 }},
      {{ label: 'Users Logged (≥1 check)', data: {json.dumps([fp_mapped_vs_logged[fp]['logged_users'] for fp in ['FP-1','FP-2','FP-3','FP-4','FP-5']])}, backgroundColor: '#38a169', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Users' }} }} }} }}
}});

// Depth Mapped vs Logged
new Chart(document.getElementById('chartDepthMappedLogged'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(list(depth_stats.keys()))},
    datasets: [
      {{ label: 'Selections (Mapped)', data: {json.dumps([depth_stats[k]['mapped'] for k in depth_stats])}, backgroundColor: '#93c5fd', borderRadius: 4 }},
      {{ label: 'Checked Logs', data: {json.dumps([depth_stats[k]['checked'] for k in depth_stats])}, backgroundColor: '#38a169', borderRadius: 4 }},
      {{ label: 'Unchecked Logs', data: {json.dumps([depth_stats[k]['unchecked'] for k in depth_stats])}, backgroundColor: '#feb2b2', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// Consistency Distribution
new Chart(document.getElementById('chartConsistency'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(consistency_order)},
    datasets: [{{ label: 'Users', data: {json.dumps(consistency_values)}, backgroundColor: ['#e2e8f0','#fed7d7','#feebc8','#fefcbf','#c6f6d5','#bee3f8'], borderRadius: 4 }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ title: {{ display: true, text: 'Users' }}, beginAtZero: true }}, x: {{ title: {{ display: true, text: 'Consistency Band' }} }} }} }}
}});

// Scatter: Tasks Mapped vs Days Logged
const scatterData = {json.dumps(scatter_data)};
new Chart(document.getElementById('chartScatter'), {{
  type: 'scatter',
  data: {{
    datasets: [
      {{ label: 'Teacher', data: scatterData.filter(d => d.role === 'Teacher').map(d => ({{x: d.x, y: d.y}})), backgroundColor: '#3b82f6', pointRadius: 5 }},
      {{ label: 'Leader', data: scatterData.filter(d => d.role === 'Leader').map(d => ({{x: d.x, y: d.y}})), backgroundColor: '#f59e0b', pointRadius: 5 }}
    ]
  }},
  options: {{ responsive: true, scales: {{ x: {{ title: {{ display: true, text: 'Tasks Mapped' }} }}, y: {{ title: {{ display: true, text: 'Days Logged' }}, beginAtZero: true }} }} }}
}});

// FP Completion Rate
const fpCompData = {json.dumps({fp: round(fp_stats[fp]['checked']/(fp_stats[fp]['checked']+fp_stats[fp]['unchecked'])*100, 1) if (fp_stats[fp]['checked']+fp_stats[fp]['unchecked']) > 0 else 0 for fp in ['FP-1','FP-2','FP-3','FP-4','FP-5']})};
new Chart(document.getElementById('chartFPCompletion'), {{
  type: 'radar',
  data: {{
    labels: ['FP-1 Unique','FP-2 Holistic','FP-3 Reflective','FP-4 Assessment','FP-5 Collaboration'],
    datasets: [{{ label: 'Completion %', data: Object.values(fpCompData),
      backgroundColor: 'rgba(56,161,105,0.2)', borderColor: '#38a169', pointBackgroundColor: '#38a169', borderWidth: 2 }}]
  }},
  options: {{ responsive: true, scales: {{ r: {{ beginAtZero: true, max: 100 }} }} }}
}});

// Table Filter
function applyFilters() {{
  const search = document.getElementById('filterSearch').value.toLowerCase();
  const role = document.getElementById('filterRole').value;
  const activity = document.getElementById('filterActivity').value;
  const rows = document.querySelectorAll('#userTableBody tr');
  let count = 0;
  rows.forEach(row => {{
    const name = row.dataset.name || '';
    const rRole = row.dataset.role || '';
    const branch = row.dataset.branch || '';
    const days = parseInt(row.dataset.days) || 0;
    let show = true;
    if (search && !name.includes(search) && !branch.includes(search)) show = false;
    if (role && rRole !== role) show = false;
    if (activity === 'active' && days === 0) show = false;
    if (activity === 'zero' && days > 0) show = false;
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
  const tbody = document.getElementById('userTableBody');
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

OUTPUT_HTML.write_text(html, encoding='utf-8')
print(f"Dashboard written to {OUTPUT_HTML} ({len(html)//1024}KB)")
print(f"  {total_users} users, {active_users} active, {total_log_entries} log entries")
