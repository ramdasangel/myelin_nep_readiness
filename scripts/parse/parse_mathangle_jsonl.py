#!/usr/bin/env python3
"""Parse Mathangle extraction output into 3 JSONL files.

Reads:  assets/myelin_stat_ro/mathangle_extraction.txt (raw mongosh output)
Writes: /tmp/mathangle_raw.jsonl
        /tmp/mathangle_exit_levels.jsonl
        /tmp/mathangle_indecision.jsonl
"""
import os

RAW_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'myelin_stat_ro', 'mathangle_extraction.txt')

with open(RAW_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

def extract_jsonl(content, start_marker, end_marker):
    s = content.index(start_marker) + len(start_marker)
    e = content.index(end_marker)
    lines = [line.strip() for line in content[s:e].strip().split('\n') if line.strip()]
    return lines

raw_lines = extract_jsonl(content, 'JSONL_START_RAW\n', '\nJSONL_END_RAW')
exit_lines = extract_jsonl(content, 'JSONL_START_EXIT\n', '\nJSONL_END_EXIT')
indecision_lines = extract_jsonl(content, 'JSONL_START_INDECISION\n', '\nJSONL_END_INDECISION')

for path, lines, label in [
    ('/tmp/mathangle_raw.jsonl', raw_lines, 'raw'),
    ('/tmp/mathangle_exit_levels.jsonl', exit_lines, 'exit_levels'),
    ('/tmp/mathangle_indecision.jsonl', indecision_lines, 'indecision'),
]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote {len(lines)} lines to {path} ({label})")

print("\nDone!")
