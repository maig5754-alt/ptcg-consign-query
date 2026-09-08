#!/usr/bin/env python3
"""Merge spu_images.json into data.js img fields."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "data.js"
IMAGES = ROOT / "spu_images.json"


def main() -> None:
    text = DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"(window\.SPU_DATA\s*=\s*)(\[.*\])(\s*;)", text, re.S)
    if not m:
        raise SystemExit("cannot parse window.SPU_DATA from data.js")
    data = json.loads(m.group(2))
    imgs = json.loads(IMAGES.read_text(encoding="utf-8")) if IMAGES.exists() else {}
    for d in data:
        spu = str(d.get("spu", ""))
        if spu in imgs and imgs[spu]:
            d["img"] = imgs[spu]
        d.setdefault("img", "")
        if not d.get("series"):
            d["series"] = "未标注"
        if not d.get("rarities"):
            raw = str(d.get("rarity") or "")
            parts = [p.strip() for p in re.split(r"[,，]", raw) if p.strip()]
            cleaned = []
            for p in parts:
                p = re.sub(r"/（[^）]*）", "", p)
                p = re.sub(r"/\([^)]*\)", "", p)
                p = p.strip()
                if p and p not in cleaned:
                    cleaned.append(p)
            d["rarities"] = cleaned
    header = (
        "// SPU 名单：新增请插到数组最前面。字段见 README。\n"
        "// 系列为空时使用「未标注」。稀有度多值用逗号分隔，页面会拆开筛选。\n"
    )
    DATA_JS.write_text(
        header + "window.SPU_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print("updated", DATA_JS, "items=", len(data), "with_img=", sum(1 for d in data if d.get("img")))


if __name__ == "__main__":
    main()
