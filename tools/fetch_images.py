#!/usr/bin/env python3
"""Fetch og:image for SPUs listed in data.js → spu_images.json"""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "data.js"
OUT = ROOT / "spu_images.json"
UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)
OG_RE = re.compile(
    r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']|'
    r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
    re.I,
)


def load_spus() -> list[str]:
    text = DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"window\.SPU_DATA\s*=\s*(\[.*\])\s*;", text, re.S)
    if not m:
        raise SystemExit("cannot parse window.SPU_DATA from data.js")
    data = json.loads(m.group(1))
    return [str(d["spu"]) for d in data if d.get("spu")]


def fetch_one(spu: str, ctx: ssl.SSLContext) -> tuple[str, str]:
    url = f"https://qiandao.com/spu?id={spu}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            html = resp.read().decode("utf-8", "ignore")
        m = OG_RE.search(html)
        img = (m.group(1) or m.group(2)) if m else ""
        if not img:
            m2 = re.search(r'"image"\s*:\s*"(https:[^"]+)"', html)
            if m2:
                img = m2.group(1)
        return spu, img
    except Exception:
        return spu, ""


def main() -> None:
    spus = load_spus()
    cache = json.loads(OUT.read_text()) if OUT.exists() else {}
    todo = [s for s in spus if not cache.get(s)]
    print(f"total={len(spus)} cached={len(spus)-len(todo)} todo={len(todo)}")
    ctx = ssl.create_default_context()
    t0 = time.time()
    done = ok = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(fetch_one, s, ctx) for s in todo]
        for fut in as_completed(futs):
            spu, img = fut.result()
            cache[spu] = img
            done += 1
            if img:
                ok += 1
            if done % 100 == 0 or done == len(todo):
                OUT.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                print(f"{done}/{len(todo)} ok={ok} elapsed={time.time()-t0:.0f}s")
    for s in spus:
        cache.setdefault(s, "")
    OUT.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    print("filled", sum(1 for s in spus if cache.get(s)))


if __name__ == "__main__":
    main()
