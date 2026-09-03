# -*- coding: utf-8 -*-
"""构建脚本：生成 .pptx 与逐页 PNG 预览 + 预览索引页。

用法：
    python3 build.py            # 全量构建
    python3 build.py --only 03-hnad   # 只渲染指定页（调试）
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deckkit import layout, theme, to_png, to_pptx  # noqa: E402
import slides  # noqa: E402

OUT = os.path.join(HERE, "output")
PREVIEW = os.path.join(OUT, "preview")
PPTX = os.path.join(OUT, "组会汇报_高效好氧降氨菌的筛选机制解析及堆肥应用.pptx")

TITLE = "高效好氧降氨菌的筛选、机制解析及其在堆肥减排保氮中的应用"


def ensure_preview_font():
    """预览字体（Droid Sans Fallback）缺失时，从 PyMuPDF 内置字体抽取。"""
    path = os.path.join(HERE, "deckkit", theme.F_PREVIEW)
    if os.path.exists(path):
        return
    import pymupdf
    buf = pymupdf.Font("china-s").buffer
    with open(path, "wb") as f:
        f.write(bytes(buf))


def build(only=None):
    ensure_preview_font()
    os.makedirs(PREVIEW, exist_ok=True)
    layout.reset_warnings()
    prs = to_pptx.new_deck(TITLE, author="[你的名字]",
                           subject="研究生组会汇报",
                           comments="本 PPT 由 deckkit 版式引擎生成，全部形状与文本均可编辑。")
    rnd = to_png.PngRenderer(scale=3.0, out_scale=2.0)
    done = []
    for fn, name in zip(slides.ALL, slides.NAMES):
        if only and name != only:
            continue
        cv = layout.Canvas(name, bg=theme.WHITE)
        fn(cv)
        rnd.render(cv, os.path.join(PREVIEW, f"slide-{name}.png"))
        if not only:
            to_pptx.render(cv, prs)
        done.append(name)
    if not only:
        prs.save(PPTX)
        _index(done)
    if not os.path.exists(os.path.join(HERE, "assets", "lab-logo.png")):
        print("提示：未找到 assets/lab-logo.png，本页组跳过右上角 logo。"
              "将实验室 logo 原图放到该路径后重跑 build.py 即可。")
    ws = layout.warnings()
    if ws:
        print("== 版式警告 ==")
        for w in ws:
            print("  ", w)
    else:
        print("无版式溢出警告。")
    return done


def _index(names):
    rows = "\n".join(
        f'<figure><a href="slide-{n}.png"><img src="slide-{n}.png" alt="{n}"></a>'
        f'<figcaption>{i + 1:02d} · {n}</figcaption></figure>'
        for i, n in enumerate(names))
    html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} · 预览</title><style>
body{{margin:0;background:#0e1620;color:#dfe7ee;font:14px/1.6 "Microsoft YaHei","PingFang SC",sans-serif}}
header{{padding:28px 32px 8px}}h1{{font-size:19px;margin:0 0 6px}}p{{margin:0;color:#8fa2b3}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:22px;padding:22px 32px 48px}}
figure{{margin:0}}figure img{{width:100%;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.45);display:block}}
figcaption{{padding:8px 2px 0;color:#8fa2b3;font-size:12px}}
a{{text-decoration:none}}</style></head><body>
<header><h1>{TITLE}</h1><p>研究生组会汇报 · 逐页预览（PNG 与 .pptx 版式一致）· 共 {len(names)} 页</p></header>
<main>{rows}</main></body></html>"""
    with open(os.path.join(PREVIEW, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    print("built:", build(only))
