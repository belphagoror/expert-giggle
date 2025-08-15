
# SPDX-License-Identifier: Apache-2.0
import sys, re, json, pathlib

RAW = pathlib.Path("corpus/raw")
CLEAN = pathlib.Path("corpus/clean")
CLEAN.mkdir(parents=True, exist_ok=True)

index = []
for p in sorted(RAW.glob("*.md")):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    # strip markdown headings and horizontal rules
    txt = re.sub(r"^#{1,6}\s+.*$", "", txt, flags=re.M)
    txt = re.sub(r"`{3}.*?`{3}", "", txt, flags=re.S)
    txt = re.sub(r"\r\n", "\n", txt)
    # drop repeated blank lines
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    # trim leading/trailing space
    txt = txt.strip()
    out = CLEAN / (p.stem + ".txt")
    out.write_text(txt, encoding="utf-8")
    index.append({
        "id": p.stem,
        "file_md": str(p),
        "file_txt": str(out),
        "chars": len(txt),
        "words": len(re.findall(r"\b\w+\b", txt)),
    })

(pathlib.Path("corpus/index.json")).write_text(json.dumps(index, indent=2), encoding="utf-8")
print(f"[mk_corpus] processed {len(index)} files")
