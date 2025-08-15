
# SPDX-License-Identifier: Apache-2.0
import sys, json, pathlib, statistics as stats
from collections import defaultdict

def main():
    results = []
    for line in open("experiments/results.jsonl","r",encoding="utf-8"):
        results.append(json.loads(line))
    by_cfg = defaultdict(list)
    for r in results:
        key = tuple(sorted((k,v) for k,v in r.items() if k in ("level","k_gloss","gloss_policy","l5_chunk") and v is not None))
        by_cfg[key].append(r)
    rows = []
    for key, arr in by_cfg.items():
        level = next(v for k,v in key if k=="level")
        cfg = {k:v for k,v in key}
        med_raw = int(stats.median(r["bytes_raw"] for r in arr))
        med_gz  = int(stats.median(r["bytes_gzip"] for r in arr))
        rows.append({"level":level, **cfg, "median_bytes_raw":med_raw, "median_bytes_gzip":med_gz, "n":len(arr)})
    rows.sort(key=lambda x: (x["level"], x.get("k_gloss",0), str(x.get("gloss_policy","")), x.get("l5_chunk",0)))
    # write a markdown table
    lines = ["# Experiment summary\n"]
    lines.append("| level | k_gloss | gloss_policy | l5_chunk | median_bytes_raw | median_bytes_gzip | n |")
    lines.append("|---|---:|---|---:|---:|---:|---:|")
    for r in rows:
        lines.append(f"| {r['level']} | {r.get('k_gloss','')} | {r.get('gloss_policy','')} | {r.get('l5_chunk','')} | {r['median_bytes_raw']} | {r['median_bytes_gzip']} | {r['n']} |")
    pathlib.Path("experiments/report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("[metrics] wrote experiments/report.md")

if __name__ == "__main__":
    main()
