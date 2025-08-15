
# SPDX-License-Identifier: Apache-2.0
import sys, json, pathlib, hashlib

def sha256s(s): return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

def union_coverage(chunks, spans):
    # per-chunk union
    id2len = {c["id"]: c["len"] for c in chunks}
    by_chunk = {}
    for s in spans:
        ch = s["chunk"]; a = int(s["start"]); b = int(s["end"])
        L = id2len.get(ch, 0)
        a = max(0, min(a, L)); b = max(0, min(b, L))
        if b > a: by_chunk.setdefault(ch, []).append((a,b))
    covered = 0
    for ch, ivs in by_chunk.items():
        ivs.sort()
        ca, cb = ivs[0]
        for a,b in ivs[1:]:
            if a <= cb: cb = max(cb, b)
            else: covered += (cb - ca); ca, cb = a, b
        covered += (cb - ca)
    total = sum(id2len.values()) or 1
    return covered/total

def main(txt_glob, l5_glob):
    import glob, os
    ok = True
    texts = {pathlib.Path(p).stem: open(p,"r",encoding="utf-8").read() for p in glob.glob(txt_glob)}
    for jp in glob.glob(l5_glob):
        doc = json.load(open(jp,"r",encoding="utf-8"))
        title = pathlib.Path(jp).name.split(".")[1]
        txt = texts.get(title)
        if not txt:
            print(f"[SKIP] {jp}: no matching text for {title}")
            continue
        tm = doc.get("text_map") or {}
        chunks = tm.get("chunks") or []
        # verify chunk hashes
        ok_hash = True
        i=0
        for c in chunks:
            part = txt[i:i+c["len"]]; i += c["len"]
            h = sha256s(part)
            if h != c["hash"]:
                print(f"[FAIL] {jp}: chunk {c['id']} hash mismatch")
                ok_hash = False
                ok = False
                break
        # coverage
        cov = union_coverage(chunks, tm.get("spans") or [])
        if abs(cov - (tm.get("coverage") or 0)) > 0.01:
            print(f"[WARN] {jp}: coverage field {tm.get('coverage')} vs recomputed {cov:.3f}")
        tol = tm.get("loss_tolerance")
        if tol is None or cov + tol + 1e-9 < 1.0:
            print(f"[FAIL] {jp}: coverage {cov:.3f} < 1 - loss_tolerance {tol}")
            ok = False
        if ok_hash:
            print(f"[OK]   {jp}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: rt_l5_text.py <corpus/clean/*.txt> <out/L5.*.json>")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
