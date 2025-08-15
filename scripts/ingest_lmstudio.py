# SPDX-License-Identifier: Apache-2.0
import sys, json, argparse, pathlib, requests
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:1234/v1")
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt", default="prompts/ingest_prompt.txt")
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", default="events.ndjson")
    ap.add_argument("--max_tokens", type=int, default=512)
    args = ap.parse_args()
    sys_prompt = pathlib.Path(args.prompt).read_text(encoding="utf-8")
    user_text  = pathlib.Path(args.text).read_text(encoding="utf-8")
    payload = {"model": args.model,
               "messages":[{"role":"system","content":sys_prompt},{"role":"user","content":user_text}],
               "temperature":0,"top_p":1.0,"seed":42,"max_tokens":args.max_tokens,"stream":False}
    r = requests.post(f"{args.base}/chat/completions", json=payload, timeout=300)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    pathlib.Path(args.out).write_text(content.strip()+"\n", encoding="utf-8")
    print(args.out)
if __name__ == "__main__":
    main()
