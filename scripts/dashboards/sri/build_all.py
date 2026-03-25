#!/usr/bin/env python3
"""
Build All SRI Dashboards — orchestrator.
Runs the unified pipeline then all 7 dashboard builders.
"""

import os
import sys
import subprocess
import time

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRI_DIR = os.path.dirname(os.path.abspath(__file__))


def run(label, script_path):
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=BASE, capture_output=True, text=True
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"  FAIL ({elapsed:.1f}s)")
        print(result.stderr[-500:] if result.stderr else "no stderr")
        return False
    print(f"  {label} ({elapsed:.1f}s)")
    return True


def main():
    print("=" * 60)
    print("  SRI Dashboard Suite — Full Build")
    print("=" * 60)

    # Step 1: Run unified pipeline
    print("\n[1/2] Running unified pipeline...")
    ok = run("Pipeline", os.path.join(BASE, "src", "sri_unified_pipeline.py"))
    if not ok:
        print("Pipeline failed — aborting dashboard builds.")
        return

    # Step 2: Run all dashboard builders
    print("\n[2/2] Building dashboards...")
    builders = sorted([
        f for f in os.listdir(SRI_DIR)
        if f.startswith("build_") and f.endswith(".py") and f != "build_all.py"
    ])

    success = 0
    for builder in builders:
        path = os.path.join(SRI_DIR, builder)
        ok = run(builder, path)
        if ok:
            success += 1

    # Summary
    out_dir = os.path.join(BASE, "output", "dashboards", "sri")
    files = sorted(f for f in os.listdir(out_dir) if f.endswith(".html"))
    total_size = sum(os.path.getsize(os.path.join(out_dir, f)) for f in files)

    print(f"\n{'=' * 60}")
    print(f"  Done: {success}/{len(builders)} dashboards built")
    print(f"  Output: {out_dir}/")
    for f in files:
        sz = os.path.getsize(os.path.join(out_dir, f)) / 1024
        print(f"    {f} ({sz:.0f} KB)")
    print(f"  Total: {total_size / 1024:.0f} KB")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
