#!/usr/bin/env python3
"""Build the Stage 5 Micro-Intervention Task Mapping Dashboard HTML.

Reads:
  output/micro_intervention_report.csv   — user-task mapping (DES only)

Writes:
  output/task_mapping_dashboard.html     — self-contained HTML dashboard

Run:
  python3 scripts/build_task_mapping_dashboard.py
"""
import csv
from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parent.parent
TASK_MAPPING_CSV = BASE / "output" / "micro_intervention_report.csv"
OUTPUT_HTML = BASE / "output" / "task_mapping_dashboard.html"

GENERATED_DATE = date.today().isoformat()  # e.g. 2026-03-02

# ── Full ISO mapping timestamps (userId → UserTaskMapping.createdAt) ──
# Update by running scripts/extract_mapping_dates_v2.js on prod when new
# users enroll, then appending the results to this dict.
MAPPING_DATES = {
    # Batch 1 — 2026-02-03
    '696ddd09c6f1e9689723f2b4': '2026-02-03T10:12:11.847Z',
    '696dc548c6f1e9689723af89': '2026-02-03T10:12:17.699Z',
    '697219bfab8e501024780612': '2026-02-03T10:12:19.455Z',
    '696ddcde7c028268c457db57': '2026-02-03T10:12:20.324Z',
    '696ddc927c028268c457d8b1': '2026-02-03T10:12:21.115Z',
    '6972199d5dab9a102eb39826': '2026-02-03T10:12:23.790Z',
    '6971e5305dab9a102eb1f2c8': '2026-02-03T10:12:23.943Z',
    '697219805dab9a102eb396b0': '2026-02-03T10:12:25.185Z',
    '696ddc99c6f1e9689723ef31': '2026-02-03T10:12:31.642Z',
    '6981c4096e1ccd12c7ec0233': '2026-02-03T10:12:37.067Z',
    '6971a29002a54777460225f2': '2026-02-03T10:12:54.248Z',
    '6971fb745dab9a102eb2b1ad': '2026-02-03T10:13:08.595Z',
    '6971a89d02a54777460240a8': '2026-02-03T10:13:08.801Z',
    '6971fb855dab9a102eb2b271': '2026-02-03T10:13:26.239Z',
    '6971dfe3ab8e501024764488': '2026-02-03T10:14:30.722Z',
    '696ddca8c6f1e9689723efd3': '2026-02-03T10:14:31.624Z',
    '6971e7fbab8e501024767b33': '2026-02-03T10:14:37.678Z',
    '696ddc94c6f1e9689723ef15': '2026-02-03T10:14:39.305Z',
    '69720fde5dab9a102eb3410a': '2026-02-03T10:14:42.993Z',
    # Batch 2 — 2026-02-04
    '69722246ab8e5010247858cb': '2026-02-04T01:57:05.960Z',
    '697214f35dab9a102eb374e1': '2026-02-04T03:20:29.351Z',
    '69720d715dab9a102eb33146': '2026-02-04T03:22:10.561Z',
    '69720be1ab8e501024778e90': '2026-02-04T03:23:52.110Z',
    '69720f3a5dab9a102eb33e6b': '2026-02-04T03:23:58.490Z',
    '69724f1eab8e50102479e59a': '2026-02-04T03:26:09.809Z',
    '6971d0e7ab8e50102475973d': '2026-02-04T05:20:32.359Z',
    '696ddd4bc6f1e9689723f464': '2026-02-04T05:26:06.513Z',
    '696ddd357c028268c457dec0': '2026-02-04T05:41:27.404Z',
    '696ddc8e7c028268c457d8a1': '2026-02-04T05:41:28.602Z',
    '6971b04002a5477746025f87': '2026-02-04T05:41:28.650Z',
    '696ddc92c6f1e9689723eefc': '2026-02-04T05:41:30.987Z',
    '6971d3685dab9a102eb141f3': '2026-02-04T05:41:31.424Z',
    '6971d6885dab9a102eb17b8e': '2026-02-04T05:41:31.510Z',
    '6971b04c02a5477746026007': '2026-02-04T05:41:32.612Z',
    '6971fe145dab9a102eb2bfa5': '2026-02-04T05:41:34.072Z',
    '6971ec745dab9a102eb23576': '2026-02-04T05:41:34.259Z',
    '69708fd34f32384a3ca50f55': '2026-02-04T05:41:35.252Z',
    '697ae9896864ae3d4877bd71': '2026-02-04T05:41:36.269Z',
    '6971d23aab8e50102475a42c': '2026-02-04T05:41:37.118Z',
    '6971fd77ab8e501024772b23': '2026-02-04T05:41:40.643Z',
    '6971ff025dab9a102eb2c7ca': '2026-02-04T05:41:41.048Z',
    '6971af9002a5477746025c55': '2026-02-04T05:41:42.300Z',
    '69709080f0a6d02140822d2c': '2026-02-04T05:41:46.882Z',
    '697225665dab9a102eb40bca': '2026-02-04T05:41:49.776Z',
    '6971dadc5dab9a102eb1af24': '2026-02-04T05:41:52.263Z',
    '6971e23cab8e501024765410': '2026-02-04T05:41:55.427Z',
    '69724cdb5dab9a102eb56a2a': '2026-02-04T05:42:01.363Z',
    '697090804f32384a3ca51136': '2026-02-04T05:42:07.666Z',
    '6971f59b5dab9a102eb28083': '2026-02-04T05:42:09.888Z',
    '6971d3d2ab8e50102475bb7a': '2026-02-04T05:42:14.129Z',
    '6971b08d02a5477746026172': '2026-02-04T05:42:25.863Z',
    '6971a77c2edad4557d61a602': '2026-02-04T05:42:34.026Z',
    '69722b94ab8e501024789e49': '2026-02-04T05:43:05.558Z',
    '696de1e7c6f1e96897241a2a': '2026-02-04T05:43:30.533Z',
    '696ddce5c6f1e9689723f17f': '2026-02-04T05:45:36.112Z',
    '6971b6669f16fa0f9d680cf8': '2026-02-04T05:46:02.254Z',
    '69720006ab8e501024773922': '2026-02-04T05:50:54.852Z',
    '6971fe42ab8e501024772ff7': '2026-02-04T05:54:21.353Z',
    '6971b2dd2edad4557d61dca1': '2026-02-04T05:54:43.461Z',
    '6971b05d02a5477746026095': '2026-02-04T06:03:13.017Z',
    '697217a15dab9a102eb385da': '2026-02-04T06:10:42.133Z',
    '6971fc335dab9a102eb2b4af': '2026-02-04T07:23:31.773Z',
    '697246965dab9a102eb53bb3': '2026-02-04T07:24:42.090Z',
    '697077fdf0a6d0214081c2e8': '2026-02-04T07:26:02.176Z',
    '6971db1d5dab9a102eb1b111': '2026-02-04T08:48:58.322Z',
    '6971d8caab8e501024760818': '2026-02-04T08:49:49.384Z',
    '6971da255dab9a102eb1a78d': '2026-02-04T08:51:08.232Z',
    '69719f6602a5477746021c42': '2026-02-04T08:51:49.086Z',
    '6971db5c5dab9a102eb1b3cc': '2026-02-04T08:52:59.018Z',
    '6971d94fab8e501024760d47': '2026-02-04T08:53:35.353Z',
    '6971d992ab8e50102476110d': '2026-02-04T08:53:41.398Z',
    '6971d97dab8e501024760f79': '2026-02-04T08:54:38.305Z',
    '6971d8ed5dab9a102eb198fa': '2026-02-04T08:55:49.903Z',
    '6971af8b2edad4557d61c5fc': '2026-02-04T09:10:34.497Z',
    '6971eff35dab9a102eb25ca8': '2026-02-04T09:31:06.236Z',
    '697217e35dab9a102eb389b4': '2026-02-04T10:09:03.962Z',
    '696ddc857c028268c457d889': '2026-02-04T11:32:14.186Z',
    '6972077a5dab9a102eb3014c': '2026-02-04T11:34:17.586Z',
    '6972077a5dab9a102eb3013d': '2026-02-04T11:34:20.784Z',
    '697254c6ab8e5010247a085f': '2026-02-04T11:53:37.275Z',
    '69723b99ab8e501024795d31': '2026-02-04T11:58:33.223Z',
    '696ddca77c028268c457d966': '2026-02-04T11:59:31.292Z',
    '696ddc6ac6f1e9689723ee6e': '2026-02-04T14:18:10.791Z',
    '696ddd557c028268c457df57': '2026-02-04T14:45:27.109Z',
    # Batch 3 — 2026-02-05
    '69721109ab8e50102477b58d': '2026-02-05T07:18:12.371Z',
    '696ddd877c028268c457e150': '2026-02-05T07:20:50.298Z',
    '6971d5feab8e50102475e247': '2026-02-05T07:23:18.258Z',
    '696df9147c028268c4584268': '2026-02-05T07:23:20.543Z',
    '6971da395dab9a102eb1a89b': '2026-02-05T07:23:22.937Z',
    '6971d4f4ab8e50102475d357': '2026-02-05T07:23:24.962Z',
    '6971d76c5dab9a102eb18864': '2026-02-05T07:23:27.400Z',
    '6971d0f7ab8e501024759815': '2026-02-05T07:23:30.626Z',
    '696ddd1b7c028268c457dde3': '2026-02-05T07:23:30.755Z',
    '697238315dab9a102eb4c831': '2026-02-05T07:23:30.755Z',
    '6971e9865dab9a102eb21802': '2026-02-05T07:23:31.739Z',
    '6971b9aa9f16fa0f9d681db9': '2026-02-05T07:23:31.978Z',
    '69721d755dab9a102eb3bf29': '2026-02-05T07:23:33.345Z',
    '6969d7f9217639055d24ea97': '2026-02-05T07:23:35.445Z',
    '6971dcd9ab8e50102476316c': '2026-02-05T07:23:44.602Z',
    '696ddcc07c028268c457da95': '2026-02-05T07:23:45.242Z',
    '696ddcab7c028268c457d9a6': '2026-02-05T07:23:45.962Z',
    '6971d076ab8e5010247591cb': '2026-02-05T07:23:46.866Z',
    '6971d15eab8e501024759af5': '2026-02-05T07:23:47.253Z',
    '696ddcaec6f1e9689723f019': '2026-02-05T07:23:48.208Z',
    '696ddcad7c028268c457d9ae': '2026-02-05T07:23:48.208Z',
    '6971e15d5dab9a102eb1da4d': '2026-02-05T07:23:48.597Z',
    '6971c2bfdc25d2246ca2c3e8': '2026-02-05T07:23:49.179Z',
    '696ddd397c028268c457dec8': '2026-02-05T07:23:50.589Z',
    '6971d0775dab9a102eb1210a': '2026-02-05T07:23:55.518Z',
    '696ddd3bc6f1e9689723f3c3': '2026-02-05T07:23:56.975Z',
    '6971f954ab8e501024770b3b': '2026-02-05T07:24:06.096Z',
    '697210925dab9a102eb34729': '2026-02-05T07:24:36.586Z',
    '697210c6ab8e50102477b348': '2026-02-05T07:27:19.866Z',
    '6971d9565dab9a102eb19d4d': '2026-02-05T08:05:04.917Z',
    '69722dc0ab8e50102478ab1b': '2026-02-05T13:11:09.823Z',
    '697201485dab9a102eb2d4cb': '2026-02-05T16:10:30.705Z',
    # Batch 4 — 2026-02-06/07
    '6971d05eab8e50102475918e': '2026-02-06T04:41:46.041Z',
    '6972379bab8e501024793a54': '2026-02-06T06:41:34.489Z',
    '6971da49ab8e501024761821': '2026-02-06T07:35:04.209Z',
    '6971d569ab8e50102475d9fe': '2026-02-06T08:46:10.397Z',
    '69722d54ab8e50102478a8e7': '2026-02-07T02:29:27.606Z',
    '697236de5dab9a102eb4b9a4': '2026-02-07T06:39:38.913Z',
    '69723c365dab9a102eb4e733': '2026-02-07T06:43:56.905Z',
    '6971fe985dab9a102eb2c57c': '2026-02-07T09:03:36.452Z',
    # Batch 5 — 2026-02-09/10/11 (added 2026-03-02)
    '6971d374ab8e50102475b55d': '2026-02-09T12:16:15.335Z',
    '697c5b4b13f4105c6faa491e': '2026-02-09T12:37:18.489Z',
    '69721971ab8e501024780326': '2026-02-09T13:58:54.472Z',
    '6971e039ab8e5010247646cf': '2026-02-09T14:03:12.219Z',
    '69721988ab8e5010247803f0': '2026-02-09T14:09:28.653Z',
    '69724568ab8e50102479a232': '2026-02-09T14:16:49.034Z',
    '69721950ab8e50102478015d': '2026-02-09T14:20:37.197Z',
    '697255945dab9a102eb59def': '2026-02-09T14:21:53.686Z',
    '6972197dab8e501024780396': '2026-02-09T14:23:47.070Z',
    '697219865dab9a102eb396ed': '2026-02-09T15:00:46.210Z',
    '69721bb6ab8e501024781a5e': '2026-02-09T15:12:30.993Z',
    '697c3a0c5b12565c25b3e8df': '2026-02-09T15:39:22.086Z',
    '69721984ab8e5010247803d0': '2026-02-09T16:25:09.837Z',
    '69723c1cab8e501024796146': '2026-02-09T16:25:44.578Z',
    '6971eca3ab8e50102476abee': '2026-02-10T02:52:50.074Z',
    '6971af8a02a5477746025c41': '2026-02-10T07:06:59.428Z',
    '69722cea5dab9a102eb43aa9': '2026-02-10T10:49:38.663Z',
    '6971a68f02a5477746023591': '2026-02-11T02:59:01.289Z',
    '6971b5e69f16fa0f9d680b03': '2026-02-11T02:59:01.701Z',
    '696ddeabc6f1e96897240033': '2026-02-11T03:01:11.358Z',
    '6971ad702edad4557d61bf7c': '2026-02-11T03:18:10.656Z',
    '6971b70302a5477746028d63': '2026-02-11T03:18:13.007Z',
    '69719f4102a5477746021be2': '2026-02-11T03:18:24.199Z',
    '6971b4952edad4557d61eb25': '2026-02-11T03:18:26.848Z',
    '6971b5c49f16fa0f9d680a84': '2026-02-11T03:18:37.900Z',
    '6971ad732edad4557d61bf88': '2026-02-11T03:20:50.302Z',
    '6971b9af9f16fa0f9d681dc5': '2026-02-11T03:20:53.263Z',
    '6971ad7302a547774602557e': '2026-02-11T03:20:58.984Z',
    '69723fe3ab8e501024797c8e': '2026-02-11T03:40:56.968Z',
    '6971a5ff02a5477746023303': '2026-02-11T04:14:23.553Z',
    '69723ee8ab8e5010247975fe': '2026-02-11T06:44:11.292Z',
    '6971d89fab8e50102476053e': '2026-02-11T06:44:14.928Z',
    '69723a285dab9a102eb4dba1': '2026-02-11T06:44:16.921Z',
    '6971d68b5dab9a102eb17bb7': '2026-02-11T07:09:13.928Z',
    '697248935dab9a102eb547de': '2026-02-11T07:09:15.302Z',
    '6971d643ab8e50102475e619': '2026-02-11T07:09:20.323Z',
    '6971a5e202a54777460232a6': '2026-02-11T07:10:25.003Z',
    '69723d2a5dab9a102eb4f012': '2026-02-11T07:22:14.977Z',
    '696ddf1bc6f1e968972403d7': '2026-02-11T09:56:22.480Z',
    '6971b1ed02a5477746026b83': '2026-02-11T13:20:37.688Z',
    '6971af4a02a5477746025bd6': '2026-02-11T13:21:33.942Z',
    '6971af932edad4557d61c628': '2026-02-11T13:55:01.136Z',
    '697191a02edad4557d6157e2': '2026-02-11T14:27:57.418Z',
    '6971af8d02a5477746025c49': '2026-02-11T15:27:24.294Z',
    '696ddd40c6f1e9689723f40f': '2026-02-17T18:29:59.119Z',
}

# ── Load DES users from micro_intervention_report.csv ──
rows = []
with open(TASK_MAPPING_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['SchoolName'].strip() == 'Deccan Education Society':
            rows.append(row)

total_users = len(rows)

# ── Build CSV_RAW string (re-emit just the DES rows) ──
csv_header = 'UserId,FirstName,LastName,FullName,Role,SchoolName,BranchName,BranchCode,TasksChosenCount,TaskList,DatesLogged,TotalDaysLogged'

def csv_field(v):
    v = str(v)
    if ',' in v or '"' in v or '\n' in v:
        return '"' + v.replace('"', '""') + '"'
    return '"' + v + '"'

csv_lines = [csv_header]
for r in rows:
    csv_lines.append(','.join([
        csv_field(r['UserId']),
        csv_field(r['FirstName']),
        csv_field(r['LastName']),
        csv_field(r['FullName']),
        csv_field(r['Role']),
        csv_field(r['SchoolName']),
        csv_field(r['BranchName']),
        csv_field(r['BranchCode']),
        csv_field(r['TasksChosenCount']),
        csv_field(r['TaskList']),
        csv_field(r['DatesLogged']),
        csv_field(r['TotalDaysLogged']),
    ]))
csv_raw = '\n'.join(csv_lines)

# ── Build MAPPING_DATES JS literal ──
md_lines = ['const MAPPING_DATES = {']
for uid, iso in MAPPING_DATES.items():
    md_lines.append(f"  '{uid}': '{iso}',")
md_lines.append('};')
mapping_dates_js = '\n'.join(md_lines)

# ── HTML template ──
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage 5 — Micro-Intervention Task Mapping Dashboard</title>
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
.header {{ background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; padding: 24px 32px; }}
.header h1 {{ font-size: 22px; margin-bottom: 4px; }}
.header p {{ font-size: 13px; opacity: 0.85; }}
.container {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}

/* KPI Cards */
.kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
.kpi {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-top: 4px solid var(--accent); }}
.kpi .value {{ font-size: 36px; font-weight: 800; color: var(--primary); }}
.kpi .label {{ font-size: 12px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
.kpi.green {{ border-top-color: var(--green); }}
.kpi.green .value {{ color: var(--green); }}
.kpi.amber {{ border-top-color: var(--amber); }}
.kpi.amber .value {{ color: var(--amber); }}
.kpi.orange {{ border-top-color: var(--orange); }}
.kpi.orange .value {{ color: var(--orange); }}
.kpi.red {{ border-top-color: var(--red); }}
.kpi.red .value {{ color: var(--red); }}

/* Charts */
.chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
.chart-box {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.chart-box h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
.chart-box canvas {{ max-height: 340px; }}
.chart-box.full {{ grid-column: 1 / -1; }}

/* FP Legend */
.fp-legend {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }}
.fp-badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.fp-badge .dot {{ width: 10px; height: 10px; border-radius: 50%; }}

/* Filters */
.filter-bar {{ background: white; border: 1px solid var(--border); border-radius: 8px; padding: 14px 20px; margin-bottom: 20px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
.filter-bar label {{ font-weight: 600; font-size: 13px; color: var(--primary); }}
.filter-bar select, .filter-bar input {{ padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; }}
.filter-bar input[type="text"] {{ min-width: 200px; }}
.filter-bar .count-badge {{ margin-left: auto; background: var(--light); padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; color: var(--accent); }}

/* Table */
.table-section {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; overflow-x: auto; }}
.table-section h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
table.data {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
table.data th {{ background: var(--primary); color: white; padding: 10px 12px; text-align: left; white-space: nowrap; cursor: pointer; user-select: none; position: sticky; top: 0; }}
table.data th:hover {{ background: var(--accent); }}
table.data th .sort-icon {{ margin-left: 4px; opacity: 0.5; }}
table.data th.sorted .sort-icon {{ opacity: 1; }}
table.data td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
table.data tr:hover {{ background: var(--light); }}
table.data tr:nth-child(even) {{ background: #f8fafc; }}
table.data tr:nth-child(even):hover {{ background: var(--light); }}

/* FP Tags in table */
.fp-tag {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; margin: 1px 2px; white-space: nowrap; }}
.fp-tag.fp1 {{ background: #eef2ff; color: var(--fp1); }}
.fp-tag.fp2 {{ background: #fdf2f8; color: var(--fp2); }}
.fp-tag.fp3 {{ background: #fffbeb; color: var(--fp3); }}
.fp-tag.fp4 {{ background: #ecfdf5; color: var(--fp4); }}
.fp-tag.fp5 {{ background: #eff6ff; color: var(--fp5); }}

/* Depth tags */
.depth-tag {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; margin: 1px 2px; white-space: nowrap; background: #f1f5f9; color: #475569; }}
.depth-tag.entry {{ background: #dbeafe; color: #1e40af; }}
.depth-tag.growth {{ background: #d1fae5; color: #065f46; }}
.depth-tag.cross {{ background: #fef3c7; color: #92400e; }}

/* Task mini-list */
.task-list {{ display: flex; flex-wrap: wrap; gap: 3px; max-width: 320px; }}
.task-chip {{ display: inline-block; padding: 2px 7px; border-radius: 8px; font-size: 10px; font-weight: 600; background: #f1f5f9; color: #334155; white-space: nowrap; }}

/* Days logged bar */
.days-bar {{ display: flex; align-items: center; gap: 6px; }}
.days-bar .bar {{ height: 8px; border-radius: 4px; background: var(--green); min-width: 2px; }}
.days-bar .bar.zero {{ background: var(--border); width: 20px; }}

@media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} .kpi-row {{ grid-template-columns: 1fr 1fr; }} }}
@media (max-width: 600px) {{ .kpi-row {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>Stage 5 — Micro-Intervention Task Mapping Dashboard</h1>
  <p>Practice Trajectory Signals &nbsp;|&nbsp; 12 Tasks (T01–T12) mapped to 5 Foundational Principles &nbsp;|&nbsp; Deccan Education Society &nbsp;|&nbsp; {total_users} Users &nbsp;|&nbsp; Data through {GENERATED_DATE}</p>
</div>

<div class="container">

<!-- FP Legend -->
<div class="fp-legend">
  <div class="fp-badge"><span class="dot" style="background:var(--fp1)"></span>FP-1 Every Child is Unique</div>
  <div class="fp-badge"><span class="dot" style="background:var(--fp2)"></span>FP-2 Holistic &amp; Experiential</div>
  <div class="fp-badge"><span class="dot" style="background:var(--fp3)"></span>FP-3 Reflective Practitioner</div>
  <div class="fp-badge"><span class="dot" style="background:var(--fp4)"></span>FP-4 Assessment for Learning</div>
  <div class="fp-badge"><span class="dot" style="background:var(--fp5)"></span>FP-5 Collaboration</div>
</div>

<!-- KPI Row -->
<div class="kpi-row">
  <div class="kpi" id="kpi-total"><div class="value">—</div><div class="label">Total Users Enrolled</div></div>
  <div class="kpi green" id="kpi-active"><div class="value">—</div><div class="label">Users Who Logged ≥1 Day</div></div>
  <div class="kpi amber" id="kpi-avg-tasks"><div class="value">—</div><div class="label">Avg Tasks / User</div></div>
  <div class="kpi orange" id="kpi-teachers"><div class="value">—</div><div class="label">Teachers</div></div>
  <div class="kpi" id="kpi-leaders"><div class="value">—</div><div class="label">Leaders</div></div>
  <div class="kpi red" id="kpi-no-log"><div class="value">—</div><div class="label">Zero Logs (No Activity)</div></div>
</div>

<!-- Charts Row 1 -->
<div class="chart-grid">
  <div class="chart-box">
    <h3>Task Adoption — Users per Task</h3>
    <canvas id="chartTaskAdoption"></canvas>
  </div>
  <div class="chart-box">
    <h3>FP Coverage — Selections by Foundational Principle</h3>
    <canvas id="chartFPCoverage"></canvas>
  </div>
</div>

<!-- Charts Row 2 -->
<div class="chart-grid">
  <div class="chart-box">
    <h3>Depth Intent Distribution</h3>
    <canvas id="chartDepthIntent"></canvas>
  </div>
  <div class="chart-box">
    <h3>Tasks Chosen per User — Distribution</h3>
    <canvas id="chartTasksDist"></canvas>
  </div>
</div>

<!-- Charts Row 3 -->
<div class="chart-grid">
  <div class="chart-box">
    <h3>Role Distribution</h3>
    <canvas id="chartRole"></canvas>
  </div>
  <div class="chart-box">
    <h3>FP Coverage — Radar (Task Selections)</h3>
    <canvas id="chartFPRadar"></canvas>
  </div>
</div>

<!-- Charts Row 4: Enrollment Timeline -->
<div class="chart-grid">
  <div class="chart-box full">
    <h3>Enrollment Timeline — When Users Selected Their Tasks (mappingCreatedAt)</h3>
    <canvas id="chartEnrollTimeline"></canvas>
  </div>
</div>

<!-- Filter Bar -->
<div class="filter-bar">
  <label>Filter:</label>
  <input type="text" id="filterSearch" placeholder="Search by name, school, branch..." oninput="applyFilters()">
  <select id="filterRole" onchange="applyFilters()">
    <option value="">All Roles</option>
    <option value="Teacher">Teacher</option>
    <option value="Leader">Leader</option>
    <option value="Unknown">Unknown / Blank</option>
  </select>
  <select id="filterFP" onchange="applyFilters()">
    <option value="">All FPs</option>
    <option value="FP-1">FP-1</option>
    <option value="FP-2">FP-2</option>
    <option value="FP-3">FP-3</option>
    <option value="FP-4">FP-4</option>
    <option value="FP-5">FP-5</option>
  </select>
  <select id="filterLogged" onchange="applyFilters()">
    <option value="">All Activity</option>
    <option value="active">Has Logged ≥1 Day</option>
    <option value="zero">Zero Logs</option>
  </select>
  <span class="count-badge" id="filteredCount">{total_users} shown</span>
</div>

<!-- User Detail Table -->
<div class="table-section">
  <h3>User Task Mapping — Detail View</h3>
  <table class="data" id="userTable">
    <thead>
      <tr>
        <th onclick="sortTable(0)">#<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(1)">Name<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(2)">Role<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(3)">School / Branch (Code)<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(4)">Tasks<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(5)">FP Coverage<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(6)">Depth Intent<span class="sort-icon">↕</span></th>
        <th>Selected Tasks</th>
        <th onclick="sortTable(8)">Mapped On<span class="sort-icon">↕</span></th>
        <th onclick="sortTable(9)">Days Logged<span class="sort-icon">↕</span></th>
      </tr>
    </thead>
    <tbody id="userTableBody"></tbody>
  </table>
</div>

</div><!-- /container -->

<script>
// ══════════════════════════════════════════════════════════════════
// TASK MASTER DATA
// ══════════════════════════════════════════════════════════════════
const TASK_META = {{
  'T01': {{ label: 'Notice One Learner', fp: 'FP-1', depth: 'D1\u2192D2', depthCat: 'entry' }},
  'T02': {{ label: 'One Adjustment', fp: 'FP-1', depth: 'D2\u2192D3', depthCat: 'growth' }},
  'T03': {{ label: 'Change One Example', fp: 'FP-2', depth: 'D1\u2192D2', depthCat: 'entry' }},
  'T04': {{ label: 'Ask a Why/How', fp: 'FP-2', depth: 'D2\u2192D3', depthCat: 'growth' }},
  'T05': {{ label: 'End-of-Class Reflection', fp: 'FP-3', depth: 'D1\u2192D2', depthCat: 'entry' }},
  'T06': {{ label: 'Try One Small Change', fp: 'FP-3', depth: 'D2\u2192D3', depthCat: 'growth' }},
  'T07': {{ label: 'Quick Check', fp: 'FP-4', depth: 'D1\u2192D2', depthCat: 'entry' }},
  'T08': {{ label: 'Spot One Pattern', fp: 'FP-4', depth: 'D2\u2192D3', depthCat: 'growth' }},
  'T09': {{ label: 'Teacher Touchpoint', fp: 'FP-5', depth: 'D1\u2192D2', depthCat: 'entry' }},
  'T10': {{ label: 'Parent Signal', fp: 'FP-5', depth: 'D1\u2192D2', depthCat: 'entry' }},
  'T11': {{ label: 'Student Voice', fp: 'FP-1', depth: 'Cross-FP', depthCat: 'cross' }},
  'T12': {{ label: 'Pause & Name', fp: 'FP-4', depth: 'Cross-FP', depthCat: 'cross' }},
}};

const FP_COLORS = {{ 'FP-1': '#6366f1', 'FP-2': '#ec4899', 'FP-3': '#f59e0b', 'FP-4': '#10b981', 'FP-5': '#3b82f6' }};
const FP_NAMES = {{
  'FP-1': 'Every Child is Unique', 'FP-2': 'Holistic & Experiential',
  'FP-3': 'Reflective Practitioner', 'FP-4': 'Assessment for Learning', 'FP-5': 'Collaboration'
}};

// ══════════════════════════════════════════════════════════════════
// MAPPING DATES (userId → mappingCreatedAt from prod)
// ══════════════════════════════════════════════════════════════════
{mapping_dates_js}

// ══════════════════════════════════════════════════════════════════
// EMBEDDED CSV DATA
// ══════════════════════════════════════════════════════════════════
const CSV_RAW = `{csv_raw}`;

// ══════════════════════════════════════════════════════════════════
// PARSE CSV
// ══════════════════════════════════════════════════════════════════
function parseCSV(raw) {{
  const lines = raw.trim().split('\\n');
  const rows = [];
  for (let i = 1; i < lines.length; i++) {{
    const line = lines[i];
    const fields = [];
    let inQuote = false, field = '';
    for (let c = 0; c < line.length; c++) {{
      const ch = line[c];
      if (ch === '"') {{ inQuote = !inQuote; }}
      else if (ch === ',' && !inQuote) {{ fields.push(field); field = ''; }}
      else {{ field += ch; }}
    }}
    fields.push(field);
    if (fields.length < 10) continue;
    const taskListRaw = fields[9] || '';
    const taskCodes = taskListRaw.split(' | ').map(t => t.split('-')[0].trim()).filter(t => t.startsWith('T'));
    const uid = fields[0];
    const mappingISO = MAPPING_DATES[uid] || '';
    const mappingDate = mappingISO ? mappingISO.split('T')[0] : '';
    rows.push({{
      userId: uid,
      firstName: fields[1] || '',
      lastName: fields[2] || '',
      fullName: (fields[1] + ' ' + fields[2]).trim(),
      role: fields[4] || '',
      schoolName: fields[5] || '',
      branchName: fields[6] || '',
      branchCode: fields[7] || '',
      tasksCount: parseInt(fields[8]) || taskCodes.length,
      taskCodes: taskCodes,
      totalDaysLogged: parseInt(fields[11]) || 0,
      mappingDate: mappingDate,
    }});
  }}
  return rows;
}}

let ALL_DATA = parseCSV(CSV_RAW);
let filteredData = [...ALL_DATA];

// ══════════════════════════════════════════════════════════════════
// COMPUTE & RENDER
// ══════════════════════════════════════════════════════════════════
function getUserFPs(taskCodes) {{
  const fps = new Set();
  taskCodes.forEach(tc => {{ if (TASK_META[tc]) fps.add(TASK_META[tc].fp); }});
  return [...fps].sort();
}}
function getUserDepths(taskCodes) {{
  const depths = new Set();
  taskCodes.forEach(tc => {{ if (TASK_META[tc]) depths.add(TASK_META[tc].depth); }});
  return [...depths].sort();
}}

function renderKPIs() {{
  const total = ALL_DATA.length;
  const active = ALL_DATA.filter(u => u.totalDaysLogged > 0).length;
  const avgTasks = (ALL_DATA.reduce((s, u) => s + u.tasksCount, 0) / total).toFixed(1);
  const teachers = ALL_DATA.filter(u => u.role === 'Teacher').length;
  const leaders = ALL_DATA.filter(u => u.role === 'Leader').length;
  const noLog = ALL_DATA.filter(u => u.totalDaysLogged === 0).length;

  document.querySelector('#kpi-total .value').textContent = total;
  document.querySelector('#kpi-active .value').textContent = active;
  document.querySelector('#kpi-avg-tasks .value').textContent = avgTasks;
  document.querySelector('#kpi-teachers .value').textContent = teachers;
  document.querySelector('#kpi-leaders .value').textContent = leaders;
  document.querySelector('#kpi-no-log .value').textContent = noLog;
}}

function renderCharts() {{
  // 1. Task Adoption
  const taskCounts = {{}};
  Object.keys(TASK_META).forEach(tc => taskCounts[tc] = 0);
  ALL_DATA.forEach(u => u.taskCodes.forEach(tc => {{ if (taskCounts[tc] !== undefined) taskCounts[tc]++; }}));
  const taskKeys = Object.keys(TASK_META);
  const taskLabels = taskKeys.map(tc => tc + ' ' + TASK_META[tc].label);
  const taskValues = taskKeys.map(tc => taskCounts[tc]);
  const taskColors = taskKeys.map(tc => FP_COLORS[TASK_META[tc].fp]);

  new Chart(document.getElementById('chartTaskAdoption'), {{
    type: 'bar',
    data: {{ labels: taskLabels, datasets: [{{ label: 'Users', data: taskValues, backgroundColor: taskColors, borderRadius: 4 }}] }},
    options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }},
      scales: {{ x: {{ title: {{ display: true, text: 'Number of Users' }} }} }} }}
  }});

  // 2. FP Coverage
  const fpCounts = {{ 'FP-1': 0, 'FP-2': 0, 'FP-3': 0, 'FP-4': 0, 'FP-5': 0 }};
  ALL_DATA.forEach(u => u.taskCodes.forEach(tc => {{ if (TASK_META[tc]) fpCounts[TASK_META[tc].fp]++; }}));
  const fpKeys = Object.keys(fpCounts);
  new Chart(document.getElementById('chartFPCoverage'), {{
    type: 'bar',
    data: {{ labels: fpKeys.map(f => f + ' ' + FP_NAMES[f]),
      datasets: [{{ label: 'Task Selections', data: fpKeys.map(f => fpCounts[f]),
        backgroundColor: fpKeys.map(f => FP_COLORS[f]), borderRadius: 6 }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }},
      scales: {{ y: {{ title: {{ display: true, text: 'Total Selections' }} }} }} }}
  }});

  // 3. Depth Intent
  const depthCounts = {{ 'D1\u2192D2 (Entry)': 0, 'D2\u2192D3 (Growth)': 0, 'Cross-FP': 0 }};
  ALL_DATA.forEach(u => u.taskCodes.forEach(tc => {{
    if (!TASK_META[tc]) return;
    const d = TASK_META[tc].depthCat;
    if (d === 'entry') depthCounts['D1\u2192D2 (Entry)']++;
    else if (d === 'growth') depthCounts['D2\u2192D3 (Growth)']++;
    else depthCounts['Cross-FP']++;
  }}));
  new Chart(document.getElementById('chartDepthIntent'), {{
    type: 'doughnut',
    data: {{ labels: Object.keys(depthCounts),
      datasets: [{{ data: Object.values(depthCounts),
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'], borderWidth: 2, borderColor: '#fff' }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});

  // 4. Tasks Chosen Distribution
  const distBuckets = {{}};
  ALL_DATA.forEach(u => {{ const k = u.tasksCount; distBuckets[k] = (distBuckets[k] || 0) + 1; }});
  const distKeys = Object.keys(distBuckets).map(Number).sort((a, b) => a - b);
  new Chart(document.getElementById('chartTasksDist'), {{
    type: 'bar',
    data: {{ labels: distKeys.map(k => k + ' tasks'),
      datasets: [{{ label: 'Users', data: distKeys.map(k => distBuckets[k]),
        backgroundColor: '#6366f1', borderRadius: 6 }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }},
      scales: {{ x: {{ title: {{ display: true, text: 'Tasks Selected' }} }}, y: {{ title: {{ display: true, text: 'Users' }} }} }} }}
  }});

  // 5. Role distribution
  const roleCounts = {{ Teacher: 0, Leader: 0, Unknown: 0 }};
  ALL_DATA.forEach(u => {{
    if (u.role === 'Teacher') roleCounts.Teacher++;
    else if (u.role === 'Leader') roleCounts.Leader++;
    else roleCounts.Unknown++;
  }});
  new Chart(document.getElementById('chartRole'), {{
    type: 'doughnut',
    data: {{ labels: Object.keys(roleCounts),
      datasets: [{{ data: Object.values(roleCounts),
        backgroundColor: ['#3b82f6', '#f59e0b', '#94a3b8'], borderWidth: 2, borderColor: '#fff' }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});

  // 6. Enrollment Timeline
  const dateBuckets = {{}};
  ALL_DATA.forEach(u => {{
    const d = u.mappingDate || 'Unknown';
    dateBuckets[d] = (dateBuckets[d] || 0) + 1;
  }});
  const dateKeys = Object.keys(dateBuckets).filter(d => d !== 'Unknown').sort();
  if (dateBuckets['Unknown']) dateKeys.push('Unknown');
  const cumulative = [];
  let runningTotal = 0;
  dateKeys.forEach(d => {{ runningTotal += dateBuckets[d]; cumulative.push(runningTotal); }});

  new Chart(document.getElementById('chartEnrollTimeline'), {{
    type: 'bar',
    data: {{
      labels: dateKeys.map(d => d === 'Unknown' ? 'Unknown' : d.replace('2026-', '')),
      datasets: [
        {{ label: 'New Enrollments', data: dateKeys.map(d => dateBuckets[d]),
          backgroundColor: '#6366f1', borderRadius: 4, order: 2 }},
        {{ label: 'Cumulative', data: cumulative, type: 'line',
          borderColor: '#e53e3e', backgroundColor: 'rgba(229,62,62,0.1)',
          pointBackgroundColor: '#e53e3e', borderWidth: 2, tension: 0.3, fill: true, order: 1 }}
      ]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ position: 'top' }} }},
      scales: {{
        x: {{ title: {{ display: true, text: 'Date' }} }},
        y: {{ title: {{ display: true, text: 'Users' }}, beginAtZero: true }}
      }}
    }}
  }});

  // 7. FP Radar
  const fpUserCoverage = {{ 'FP-1': 0, 'FP-2': 0, 'FP-3': 0, 'FP-4': 0, 'FP-5': 0 }};
  ALL_DATA.forEach(u => {{
    const fps = new Set();
    u.taskCodes.forEach(tc => {{ if (TASK_META[tc]) fps.add(TASK_META[tc].fp); }});
    fps.forEach(fp => fpUserCoverage[fp]++);
  }});
  new Chart(document.getElementById('chartFPRadar'), {{
    type: 'radar',
    data: {{ labels: fpKeys.map(f => f + ' ' + FP_NAMES[f]),
      datasets: [{{ label: 'Users Covering This FP', data: fpKeys.map(f => fpUserCoverage[f]),
        backgroundColor: 'rgba(99, 102, 241, 0.2)', borderColor: '#6366f1', pointBackgroundColor: '#6366f1', borderWidth: 2 }}] }},
    options: {{ responsive: true, scales: {{ r: {{ beginAtZero: true }} }},
      plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});
}}

// ══════════════════════════════════════════════════════════════════
// TABLE
// ══════════════════════════════════════════════════════════════════
function fpTagHTML(fp) {{
  const cls = fp.replace('-', '').toLowerCase();
  return '<span class="fp-tag ' + cls + '">' + fp + '</span>';
}}
function depthTagHTML(depth) {{
  let cls = 'entry';
  if (depth.includes('D2\u2192D3')) cls = 'growth';
  else if (depth.includes('Cross')) cls = 'cross';
  return '<span class="depth-tag ' + cls + '">' + depth + '</span>';
}}

function renderTable() {{
  const tbody = document.getElementById('userTableBody');
  let html = '';
  filteredData.forEach((u, i) => {{
    const name = u.fullName === 'Unknown Unknown' ? '<em style="color:var(--muted)">Unknown</em>' : escH(u.fullName);
    const school = u.schoolName || '\u2014';
    const branch = u.branchName || '\u2014';
    const code = u.branchCode ? '(' + u.branchCode + ')' : '';
    const location = escH(school) + ' / ' + escH(branch) + ' ' + escH(code);
    const role = u.role || '<span style="color:var(--muted)">\u2014</span>';
    const fps = getUserFPs(u.taskCodes);
    const depths = getUserDepths(u.taskCodes);
    const taskChips = u.taskCodes.map(tc => '<span class="task-chip">' + tc + '</span>').join('');
    const maxDays = 21;
    const barW = Math.max(2, (u.totalDaysLogged / maxDays) * 120);
    const barCls = u.totalDaysLogged === 0 ? 'zero' : '';
    const mappedOn = u.mappingDate ? u.mappingDate.replace('2026-', '') : '<span style="color:var(--muted)">\u2014</span>';
    html += '<tr>' +
      '<td>' + (i + 1) + '</td>' +
      '<td><strong>' + name + '</strong></td>' +
      '<td>' + role + '</td>' +
      '<td style="max-width:300px;font-size:11px">' + location + '</td>' +
      '<td style="text-align:center"><strong>' + u.tasksCount + '</strong></td>' +
      '<td>' + fps.map(fpTagHTML).join('') + '</td>' +
      '<td>' + depths.map(depthTagHTML).join('') + '</td>' +
      '<td><div class="task-list">' + taskChips + '</div></td>' +
      '<td style="white-space:nowrap;font-size:11px;font-weight:600">' + mappedOn + '</td>' +
      '<td><div class="days-bar"><div class="bar ' + barCls + '" style="width:' + barW + 'px"></div><span style="font-size:11px;font-weight:600">' + u.totalDaysLogged + '</span></div></td>' +
      '</tr>';
  }});
  tbody.innerHTML = html;
  document.getElementById('filteredCount').textContent = filteredData.length + ' shown';
}}

function escH(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

// ══════════════════════════════════════════════════════════════════
// FILTERS
// ══════════════════════════════════════════════════════════════════
function applyFilters() {{
  const search = document.getElementById('filterSearch').value.toLowerCase();
  const role = document.getElementById('filterRole').value;
  const fpFilter = document.getElementById('filterFP').value;
  const logFilter = document.getElementById('filterLogged').value;

  filteredData = ALL_DATA.filter(u => {{
    if (search) {{
      const hay = (u.fullName + ' ' + u.schoolName + ' ' + u.branchName + ' ' + u.branchCode).toLowerCase();
      if (!hay.includes(search)) return false;
    }}
    if (role === 'Teacher' && u.role !== 'Teacher') return false;
    if (role === 'Leader' && u.role !== 'Leader') return false;
    if (role === 'Unknown' && u.role !== '') return false;
    if (fpFilter) {{
      const fps = getUserFPs(u.taskCodes);
      if (!fps.includes(fpFilter)) return false;
    }}
    if (logFilter === 'active' && u.totalDaysLogged === 0) return false;
    if (logFilter === 'zero' && u.totalDaysLogged > 0) return false;
    return true;
  }});
  renderTable();
}}

// ══════════════════════════════════════════════════════════════════
// SORT
// ══════════════════════════════════════════════════════════════════
let sortCol = -1, sortAsc = true;
function sortTable(col) {{
  if (sortCol === col) sortAsc = !sortAsc;
  else {{ sortCol = col; sortAsc = true; }}

  filteredData.sort((a, b) => {{
    let va, vb;
    switch (col) {{
      case 0: va = ALL_DATA.indexOf(a); vb = ALL_DATA.indexOf(b); break;
      case 1: va = a.fullName.toLowerCase(); vb = b.fullName.toLowerCase(); break;
      case 2: va = a.role; vb = b.role; break;
      case 3: va = (a.schoolName + a.branchName).toLowerCase(); vb = (b.schoolName + b.branchName).toLowerCase(); break;
      case 4: va = a.tasksCount; vb = b.tasksCount; break;
      case 5: va = getUserFPs(a.taskCodes).length; vb = getUserFPs(b.taskCodes).length; break;
      case 6: va = getUserDepths(a.taskCodes).length; vb = getUserDepths(b.taskCodes).length; break;
      case 8: va = a.mappingDate; vb = b.mappingDate; break;
      case 9: va = a.totalDaysLogged; vb = b.totalDaysLogged; break;
      default: return 0;
    }}
    if (va < vb) return sortAsc ? -1 : 1;
    if (va > vb) return sortAsc ? 1 : -1;
    return 0;
  }});
  renderTable();
}}

// ══════════════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════════════
renderKPIs();
renderCharts();
renderTable();
</script>

</body>
</html>"""

OUTPUT_HTML.write_text(HTML, encoding='utf-8')
size_kb = OUTPUT_HTML.stat().st_size // 1024
print(f"Dashboard written to {OUTPUT_HTML} ({size_kb}KB)")
print(f"  {total_users} users | Data through {GENERATED_DATE}")
