# -*- coding: utf-8 -*-
"""组会汇报 PPT —— 全部 10 页版式（文字严格按盲测确认稿，不改写、不增删论点）。"""
from __future__ import annotations

import math

import os

from deckkit import theme as T
from deckkit.layout import Canvas, para, rich

M, CW = T.M, T.CW
TOTAL = 10
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "lab-logo.png")


def logo(cv: Canvas, dark: bool = False) -> bool:
    """每页右上角的实验室 logo（家畜生态研究室 / Livestock Ecology Lab）。

    dark=True 时（封面/尾页深蓝底）加白色圆角底卡，避免透明底缺失时发闷。
    logo 文件缺失时静默跳过，build.py 会给出提示。
    """
    if not os.path.exists(LOGO):
        return False
    from PIL import Image
    with Image.open(LOGO) as im:
        ar = im.width / im.height
    h = 30.0
    w = h * ar
    x, y = 912 - w, 20
    if dark:
        cv.rect(x - 9, y - 7, w + 18, h + 14, fill=T.WHITE, line=None, radius=9,
                shadow=True)
    cv.image(LOGO, x, y, h=h)
    return True

# ------------------------------------------------------------------ 化学式片段
def _f(base, sub=None, sup=None, color=None, bold=True):
    out = [(base, {"color": color} if color else {})]
    if sub:
        st = {"sub": True, "bold": bold}
        if color:
            st["color"] = color
        out.append((sub, st))
    if sup:
        st = {"sup": True, "bold": bold}
        if color:
            st["color"] = color
        out.append((sup, st))
    return out


def NH4(color=None, bold=True, suffix=""):
    r = _f("NH", "4", "+", color, bold)
    if suffix:
        r.append((suffix, {"color": color} if color else {}))
    return r


def NO2(color=None, bold=True, suffix=""):
    r = _f("NO", "2", "-", color, bold)
    if suffix:
        r.append((suffix, {"color": color} if color else {}))
    return r


def NO3(color=None, bold=True, suffix=""):
    r = _f("NO", "3", "-", color, bold)
    if suffix:
        r.append((suffix, {"color": color} if color else {}))
    return r


def N2(color=None, bold=True, suffix=""):
    r = _f("N", "2", None, color, bold)
    if suffix:
        r.append((suffix, {"color": color} if color else {}))
    return r


# ------------------------------------------------------------------ 页面骨架
def page(cv: Canvas, kicker: str, title, no: int):
    cv.text(M, 24, 620, 14, [para(text=kicker, size=9.5, bold=True, color=T.TEAL,
                                  spacing=1.0)])
    if isinstance(title, str):
        cv.text(M, 40, 780, 32, [para(text=title, size=20.5, bold=True, color=T.NAVY,
                                      spacing=1.05)])
    else:
        cv.text(M, 40, 780, 32, [rich(*title, size=20.5, bold=True, color=T.NAVY,
                                      spacing=1.05)])
    cv.rect(M, 78, 42, 3.5, fill=T.TEAL)
    cv.rect(M + 46, 78, 20, 3.5, fill=T.LINE)
    if not logo(cv):
        # 无 logo 时保留右上角淡灰页码装饰（与首版一致）
        cv.text(812, 20, 100, 44, [para(text=f"{no:02d}", size=30, bold=True,
                                        color="E3EAF2", align="r", spacing=1.0)])
    cv.line(M, 94, 912, 94, color=T.LINE, lw=1.0)
    cv.line(M, 508, 912, 508, color=T.LINE, lw=0.75)
    cv.text(M, 514, 640, 14, [para(text="高效好氧降氨菌的筛选、机制解析及其在堆肥减排保氮中的应用",
                                   size=8, color=T.GRAY_L, spacing=1.0)])
    cv.text(740, 514, 172, 14, [para(text=f"{no:02d} / {TOTAL}", size=8.5, color=T.GRAY,
                                     align="r", spacing=1.0)])


# ------------------------------------------------------------------ 小图标（矢量）
def icon_flask(cv, cx, cy, s, color):
    cv.path([(cx - 0.10 * s, cy - 0.46 * s), (cx - 0.10 * s, cy - 0.06 * s),
             (cx - 0.36 * s, cy + 0.40 * s), (cx + 0.36 * s, cy + 0.40 * s),
             (cx + 0.10 * s, cy - 0.06 * s), (cx + 0.10 * s, cy - 0.46 * s)],
            line=color, lw=1.6, cap="rnd")
    cv.line(cx - 0.16 * s, cy - 0.46 * s, cx + 0.16 * s, cy - 0.46 * s, color=color,
            lw=1.6, cap="rnd")
    cv.line(cx - 0.22 * s, cy + 0.16 * s, cx + 0.22 * s, cy + 0.16 * s, color=color,
            lw=1.4, cap="rnd")
    cv.ellipse(cx - 0.06 * s, cy + 0.22 * s, 0.09 * s, 0.09 * s, fill=color)


def icon_drop(cv, cx, cy, s, color):
    cv.path([(cx, cy - 0.46 * s), (cx - 0.30 * s, cy + 0.10 * s), (cx - 0.30 * s,
             cy + 0.20 * s), (cx, cy + 0.46 * s), (cx + 0.30 * s, cy + 0.20 * s),
             (cx + 0.30 * s, cy + 0.10 * s), (cx, cy - 0.46 * s)],
            line=color, lw=1.6, cap="rnd")
    cv.ellipse(cx - 0.10 * s, cy + 0.10 * s, 0.12 * s, 0.12 * s, fill=color)


def icon_temp(cv, cx, cy, s, color):
    cv.rect(cx - 0.10 * s, cy - 0.48 * s, 0.20 * s, 0.72 * s, line=color, lw=1.6,
            radius=0.10 * s)
    cv.ellipse(cx - 0.20 * s, cy + 0.22 * s, 0.40 * s, 0.40 * s, fill=color)
    cv.line(cx, cy + 0.26 * s, cx, cy - 0.18 * s, color=color, lw=2.0, cap="rnd")
    for yy in (-0.34, -0.18, -0.02):
        cv.line(cx + 0.10 * s, cy + yy * s, cx + 0.22 * s, cy + yy * s, color=color,
                lw=1.2)


def icon_wind(cv, cx, cy, s, color):
    for yy, ln in ((-0.26, 0.62), (0.0, 0.86), (0.26, 0.50)):
        cv.curve([(cx - 0.45 * s, cy + yy * s), (cx - 0.1 * s, cy + (yy - 0.10) * s),
                  (cx + ln * 0.3 * s, cy + (yy + 0.06) * s), (cx + ln * 0.5 * s,
                  cy + yy * s)], color=color, lw=1.6)


def icon_dna(cv, cx, cy, s, color):
    p1, p2 = [], []
    for i in range(25):
        t = i / 24.0
        y = cy - 0.48 * s + t * 0.96 * s
        dx = math.sin(t * math.pi * 2) * 0.26 * s
        p1.append((cx + dx, y))
        p2.append((cx - dx, y))
    cv.path(p1, line=color, lw=1.5, cap="rnd")
    cv.path(p2, line=color, lw=1.5, cap="rnd")
    for i in (5, 12, 19):
        cv.line(p1[i][0], p1[i][1], p2[i][0], p2[i][1], color=color, lw=1.2)


def icon_ban(cv, cx, cy, s, color):
    cv.ellipse(cx - 0.40 * s, cy - 0.40 * s, 0.80 * s, 0.80 * s, line=color, lw=1.8)
    cv.line(cx - 0.27 * s, cy + 0.27 * s, cx + 0.27 * s, cy - 0.27 * s, color=color,
            lw=1.8, cap="rnd")


def icon_chart(cv, cx, cy, s, color):
    cv.line(cx - 0.40 * s, cy - 0.40 * s, cx - 0.40 * s, cy + 0.40 * s, color=color,
            lw=1.5, cap="rnd")
    cv.line(cx - 0.40 * s, cy + 0.40 * s, cx + 0.44 * s, cy + 0.40 * s, color=color,
            lw=1.5, cap="rnd")
    cv.curve([(cx - 0.32 * s, cy + 0.26 * s), (cx - 0.05 * s, cy - 0.10 * s),
              (cx + 0.15 * s, cy + 0.06 * s), (cx + 0.36 * s, cy - 0.30 * s)],
             color=color, lw=1.8)


def icon_gas(cv, cx, cy, s, color):
    cv.ellipse(cx - 0.42 * s, cy - 0.10 * s, 0.36 * s, 0.36 * s, line=color, lw=1.5)
    cv.ellipse(cx - 0.16 * s, cy - 0.30 * s, 0.46 * s, 0.46 * s, line=color, lw=1.5)
    cv.ellipse(cx + 0.14 * s, cy - 0.08 * s, 0.34 * s, 0.34 * s, line=color, lw=1.5)
    cv.rect(cx - 0.34 * s, cy + 0.06 * s, 0.70 * s, 0.16 * s, fill=T.WHITE, line=None)
    cv.line(cx - 0.34 * s, cy + 0.08 * s, cx + 0.36 * s, cy + 0.08 * s, color=color,
            lw=1.5)


def icon_leaf(cv, cx, cy, s, color):
    cv.curve([(cx - 0.38 * s, cy + 0.38 * s), (cx - 0.34 * s, cy - 0.28 * s),
              (cx + 0.10 * s, cy - 0.46 * s), (cx + 0.40 * s, cy - 0.40 * s)],
             color=color, lw=1.7)
    cv.curve([(cx + 0.40 * s, cy - 0.40 * s), (cx + 0.36 * s, cy + 0.16 * s),
              (cx - 0.02 * s, cy + 0.42 * s), (cx - 0.38 * s, cy + 0.38 * s)],
             color=color, lw=1.7)
    cv.line(cx - 0.30 * s, cy + 0.30 * s, cx + 0.28 * s, cy - 0.28 * s, color=color,
            lw=1.2)


def icon_target(cv, cx, cy, s, color):
    cv.ellipse(cx - 0.42 * s, cy - 0.42 * s, 0.84 * s, 0.84 * s, line=color, lw=1.6)
    cv.ellipse(cx - 0.24 * s, cy - 0.24 * s, 0.48 * s, 0.48 * s, line=color, lw=1.4)
    cv.ellipse(cx - 0.07 * s, cy - 0.07 * s, 0.14 * s, 0.14 * s, fill=color)


# ------------------------------------------------------------------ 通用组件
def card_title(cv, x, y, w, chip_text, chip_bg, chip_fg, title, size=13.5):
    cx = x
    if chip_text:
        cw_, _ = cv.chip(x, y, chip_text, fill=chip_bg, color=chip_fg, size=9.5,
                         pad_x=8, pad_y=3.5)
        cx = x + cw_ + 9
    cv.text(cx, y - 2, w - (cx - x), 22, [para(text=title, size=size, bold=True,
                                               color=T.INK, spacing=1.0)])
    return y + 26


# ================================================================== 1 封面
def s_cover(cv: Canvas):
    cv.bg = None
    cv.rect(0, 0, 960, 540, grad=(T.NAVY_D, "#10497E", 90))
    cv.rect(0, 0, 960, 540, fill="0B2540", alpha=0.18)
    cv.ellipse(640, -190, 560, 560, line="FFFFFF", lw=1.0, alpha=0.10)
    cv.ellipse(706, -124, 428, 428, line=T.TEAL, lw=1.2, alpha=0.35)
    cv.ellipse(772, -58, 296, 296, line="FFFFFF", lw=0.8, alpha=0.10)
    nodes = [(760, 300), (838, 246), (872, 340), (788, 386), (700, 352)]
    for i in range(len(nodes) - 1):
        cv.line(nodes[i][0], nodes[i][1], nodes[i + 1][0], nodes[i + 1][1],
                color=T.TEAL, lw=1.1, alpha=0.55)
    cv.line(nodes[-1][0], nodes[-1][1], nodes[0][0], nodes[0][1], color=T.TEAL,
            lw=1.1, alpha=0.55)
    for i, (nx, ny) in enumerate(nodes):
        r = 7 if i else 10
        cv.ellipse(nx - r, ny - r, r * 2, r * 2, fill=T.TEAL if i else "FFFFFF",
                   alpha=0.9 if i else 0.95)
    cv.ellipse(778, 333, 20, 20, fill=T.NAVY_D, line=T.TEAL, lw=1.2)
    cv.text(778, 333, 20, 20, [para(text="N", size=11, bold=True, color=T.TEAL,
                                    align="c", spacing=1.0)], valign="m")
    cv.rect(0, 0, 7, 540, grad=(T.TEAL, T.TEAL_D, 90))
    cv.text(64, 54, 500, 16, [para(text="研究生组会汇报 · RESEARCH SEMINAR", size=10.5,
                                   bold=True, color="9FD8CE", spacing=1.0)])
    cv.line(64, 80, 168, 80, color=T.TEAL, lw=2.0)
    cv.text(64, 150, 700, 120, [para(text="高效好氧降氨菌的筛选、机制解析", size=35,
                                     bold=True, color="FFFFFF", spacing=1.28),
                                para(text="及其在堆肥减排保氮中的应用", size=35,
                                     bold=True, color="FFFFFF", spacing=1.28)])
    cv.rect(66, 268, 92, 4.5, fill=T.TEAL)
    cv.text(64, 288, 640, 44, [para(text="Screening and Mechanism of High-efficiency Aerobic "
                                         "Ammonia-removing Bacteria and Their Application in "
                                         "Composting for Emission Reduction and Nitrogen Retention",
                                    size=10, color="B9CBDD", spacing=1.45)])
    cv.rect(64, 372, 452, 108, fill="FFFFFF", alpha=0.10, line="FFFFFF", lw=0.9,
            radius=12)
    cv.rect(64, 372, 4.5, 108, fill=T.TEAL, radius=2.2)
    rows = [("汇报人", "[你的名字]"), ("指导教师", "[导师名字]"),
            ("汇报日期", "202X年X月X日")]
    for i, (k, v) in enumerate(rows):
        yy = 388 + i * 26
        cv.text(88, yy, 76, 20, [para(text=k, size=12, bold=True, color="9FD8CE",
                                      spacing=1.0)], valign="m")
        cv.text(168, yy, 330, 20, [para(text=v, size=12.5, bold=True, color="FFFFFF",
                                        spacing=1.0)], valign="m")
    logo(cv, dark=True)
    cv.chip(742, 470, "HN-AD · 异养硝化-好氧反硝化", fill=T.TEAL, color="FFFFFF",
            size=10, pad_x=12, pad_y=6)


# ================================================================== 2 目录
def s_toc(cv: Canvas):
    page(cv, "CONTENTS", "汇报框架", 2)
    cards = [
        ("01", "研究背景与立题依据", "Research Background",
         [("行业背景 · 堆肥“减污与保氮”痛点", "P03"),
          ("科学瓶颈 · 脱氮领域的“氧气悖论”", "P04"),
          ("解决方案 · HN-AD 菌（核心主角）", "P05")], T.NAVY),
        ("02", "当前试验流程与进展", "Current Experimental Workflow",
         [("整体策略 · 漏斗式降维筛选法", "P06"),
          ("核心实验 · 72h 氮素转化动力学评估", "P07"),
          ("指标体系 · 取样频次与四大检测指标", "P08"),
          ("预期与计划 · 成果输出与下一步工作", "P09")], T.TEAL_D),
    ]
    for i, (num, cn, en, items, col) in enumerate(cards):
        x = M + i * 452
        w = 412
        cv.card(x, 150, w, 300, fill=T.WHITE, line=T.LINE, radius=14)
        cv.rect(x, 150, w, 6, fill=col, radius=3)
        cv.text(x + 30, 180, 120, 60, [para(text=num, size=40, bold=True, color=col,
                                            spacing=1.0)])
        cv.line(x + 108, 186, x + 108, 234, color=T.LINE, lw=1)
        cv.text(x + 126, 186, w - 150, 30, [para(text=cn, size=17.5, bold=True,
                                                 color=T.NAVY, spacing=1.1)])
        cv.text(x + 126, 214, w - 150, 16, [para(text=en, size=9.5, color=T.GRAY,
                                                 spacing=1.0)])
        yy = 262
        for it, pg in items:
            cv.ellipse(x + 32, yy + 6, 7, 7, fill=col, alpha=0.85)
            cv.text(x + 50, yy - 2, w - 130, 22, [para(text=it, size=12, color=T.INK,
                                                       spacing=1.05)])
            cv.text(x + w - 74, yy - 2, 44, 22, [para(text=pg, size=10, bold=True,
                                                      color=col, align="r",
                                                      spacing=1.05)])
            yy += 34
        cv.line(x + 30, 410, x + w - 30, 410, color=T.LINE, lw=0.75)
        cv.text(x + 30, 418, w - 60, 18,
                [para(text=("3 页 · 立论：为什么必须找好氧降氨菌" if i == 0 else
                            "4 页 · 实证：筛菌 → 动力学 → 指标 → 计划"),
                      size=9.5, color=T.GRAY_L, spacing=1.0)])


# ================================================================== 3 行业背景
def s_bg(cv: Canvas):
    page(cv, "PART 01 · 研究背景与立题依据",
         "行业背景 —— 堆肥过程中的“减污与保氮”痛点", 3)
    cv.card(48, 108, 864, 54, fill=T.BG_SOFT, line=T.LINE, radius=10, shadow=False,
            bar=T.TEAL, bar_w=4)
    cv.text(70, 108, 820, 54, [rich(("资源化利用的必经之路　", {"color": T.TEAL_D}),
                                    ("好氧堆肥是目前处理农业废弃物（畜禽粪污、秸秆等）"
                                     "最主流、最经济的技术。", {}),
                                    size=12.5, color=T.INK, spacing=1.2)], valign="m")
    # 痛点一
    cv.card(48, 176, 520, 104, fill=T.WHITE, line=T.LINE, radius=12, bar=T.AMBER,
            bar_w=4)
    card_title(cv, 68, 190, 470, "痛点一", T.AMBER_L, "#9A5A12", "严重的环境臭气污染")
    cv.text(68, 222, 480, 52, [
        rich(("物料中富含的有机氮（蛋白质/尿素）在高温下迅速氨化，产生极高浓度的氨氮（", {}),
             *NH4(color=T.AMBER), ("）。", {}), size=11.5, bullet="•",
             bullet_color=T.AMBER, spacing=1.34, space_after=5),
        rich(("在堆肥的高温、偏碱性环境中，氨氮大量以", {}),
             ("氨气", {"bold": True, "color": T.AMBER}),
             ("（NH", {}), ("3", {"sub": True}), ("↑）", {}),
             ("形式挥发，导致强烈的恶臭污染。", {}),
             size=11.5, bullet="•", bullet_color=T.AMBER, spacing=1.34)])
    # 痛点二
    cv.card(48, 294, 520, 190, fill=T.WHITE, line=T.LINE, radius=12, bar=T.RED,
            bar_w=4)
    card_title(cv, 68, 310, 470, "痛点二", T.RED_L, T.RED, "核心肥效（氮素）的大量流失")
    cv.text(68, 342, 316, 110, [
        rich(("氨气挥发不仅污染环境，更导致堆肥终产物中", {}),
             ("总氮流失率高达 40%-60%", {"bold": True, "color": T.RED}),
             ("，严重降低了有机肥的农业价值。", {}),
             size=11.5, bullet="•", bullet_color=T.RED, spacing=1.36)])
    cv.line(404, 342, 404, 462, color=T.LINE, lw=0.75)
    cv.text(420, 352, 132, 16, [para(text="总氮流失率", size=9.5, color=T.GRAY,
                                     spacing=1.0)])
    cv.text(420, 372, 132, 44, [para(text="40%-60%", size=26, bold=True, color=T.RED,
                                     spacing=1.0)])
    cv.text(420, 424, 132, 30, [para(text="肥效与经济双重损失", size=8.5, color=T.GRAY_L,
                                     spacing=1.3)])
    # 右：堆体氮素去向示意
    cv.card(588, 176, 324, 308, fill=T.BG_SOFT, line=T.LINE, radius=12, shadow=True)
    cv.text(608, 190, 200, 16, [para(text="堆肥堆体氮素去向 · 示意", size=10, bold=True,
                                     color=T.GRAY, spacing=1.0)])
    cv.chip(608, 214, "NH3↑ 挥发", fill=T.AMBER_L, color="#9A5A12", size=9.5,
            pad_x=9, pad_y=4.5)
    cv.chip(694, 214, "强烈恶臭污染", fill=T.RED_L, color=T.RED, size=9.5, pad_x=9,
            pad_y=4.5)
    pile_top, pile_bot = 356, 452
    cv.poly([(628, pile_bot), (872, pile_bot), (836, pile_top), (664, pile_top)],
            fill="#A6804F", line=None)
    cv.poly([(664, pile_top), (836, pile_top), (826, pile_top + 12),
             (674, pile_top + 12)], fill="#8E6A3E", line=None)
    for dx, dy in ((700, 400), (742, 420), (790, 404), (820, 428), (760, 386)):
        cv.ellipse(dx, dy, 5, 5, fill="#7A5A33", alpha=0.55)
    cv.text(628, 414, 244, 18, [para(text="好氧堆肥堆体（高温 · 偏碱）", size=9.5,
                                     bold=True, color="FFFFFF", align="c",
                                     spacing=1.0)])
    cv.arrow(614, 322, 664, 350, color=T.GRAY, lw=1.6, head=8)
    cv.text(596, 300, 130, 16, [para(text="有机氮（蛋白质/尿素）", size=9, color=T.GRAY,
                                     spacing=1.0)])
    for k, ax in enumerate((706, 752, 798)):
        cv.arrow(ax, 348, ax + (k - 1) * 8, 262, color=T.AMBER, lw=2.0, head=9)



# ================================================================== 4 氧气悖论
def s_paradox(cv: Canvas):
    page(cv, "PART 01 · 研究背景与立题依据",
         "科学瓶颈 —— 脱氮领域的“氧气悖论”", 4)
    panels = [
        (48, T.BLUE_L, T.BLUE, "传统脱氮理论", "严格厌氧的反硝化菌",
         [("传统反硝化脱氮微生物属于", {}), ("严格厌氧菌", {"bold": True, "color": T.BLUE}),
          ("（缺氧条件才能产气脱氮）。", {})], icon_ban, T.RED),
        (508, T.TEAL_L, T.TEAL_D, "现代堆肥工艺", "强制通风 · 极度好氧",
         [("现代堆肥工艺为了发酵和升温，必须进行", {}),
          ("强制通风", {"bold": True, "color": T.TEAL_D}),
          ("（极度好氧环境）。", {})], icon_wind, T.TEAL_D),
    ]
    for x, bg, fg, chip, ttl, runs, icon, ic in panels:
        cv.card(x, 112, 404, 112, fill=T.WHITE, line=T.LINE, radius=12, bar=fg, bar_w=4)
        cv.rect(x + 330, 126, 56, 56, fill=bg, line=None, radius=14)
        icon(cv, x + 358, 154, 34, ic)
        card_title(cv, x + 20, 126, 300, chip, bg, fg, ttl, size=13.5)
        cv.text(x + 20, 158, 300, 56, [rich(*runs, size=12, bullet="•", bullet_color=fg,
                                            spacing=1.42)])
    cv.ellipse(456, 144, 48, 48, fill=T.NAVY_D, line="FFFFFF", lw=2)
    cv.text(456, 144, 48, 48, [para(text="VS", size=15, bold=True, color="FFFFFF",
                                    align="c", spacing=1.0)], valign="m")
    cv.arrow(452, 168, 424, 168, color=T.NAVY_D, lw=1.6, head=7)
    cv.arrow(508, 168, 536, 168, color=T.NAVY_D, lw=1.6, head=7)
    cv.card(48, 244, 864, 62, fill=T.RED_L, line=None, radius=10, shadow=False,
            bar=T.RED, bar_w=4)
    cv.text(70, 244, 820, 62, [rich(("核心矛盾　", {"bold": True, "color": T.RED}),
                                    ("传统脱氮菌在好氧堆肥体系中，会因", {}),
                                    ("“氧气毒害”", {"bold": True, "color": T.RED}),
                                    ("而失活，无法完成脱氮任务。", {}),
                                    size=12.5, spacing=1.2)], valign="m")
    cv.arrow(480, 312, 480, 330, color=T.GRAY_L, lw=1.6, head=8)
    cv.card(48, 336, 864, 88, fill=T.TEAL_L, line=None, radius=10, shadow=False,
            bar=T.TEAL, bar_w=4)
    cv.text(70, 336, 820, 88, [rich(("破局思路　", {"bold": True, "color": T.TEAL_D}),
                                    ("亟需寻找能够在", {}),
                                    ("高溶解氧", {"bold": True, "color": T.TEAL_D}),
                                    ("条件下，依然保持", {}),
                                    ("高效氮素转化能力", {"bold": True, "color": T.TEAL_D}),
                                    ("的特异性微生物群落。", {}),
                                    size=13, spacing=1.4)], valign="m")
    cv.chip(806, 440, "→ 见下页 HN-AD", fill=T.WHITE, color=T.TEAL_D, size=9.5,
            pad_x=10, pad_y=5)


# ================================================================== 5 HN-AD
def s_hnad(cv: Canvas):
    page(cv, "PART 01 · 研究背景与立题依据",
         "解决方案 —— HN-AD 菌（本课题的核心主角）", 5)
    cv.card(48, 108, 864, 200, fill=T.WHITE, line=T.LINE, radius=14)
    cv.text(68, 122, 420, 18, [para(text="异养硝化-好氧反硝化（HN-AD）细菌 · 同步转化路径",
                                    size=11.5, bold=True, color=T.NAVY, spacing=1.0)])
    cv.chip(636, 118, "好氧体系（高溶解氧）", fill=T.TEAL_L, color=T.TEAL_D, size=9.5,
            pad_x=9, pad_y=4.5)
    cv.chip(782, 118, "有机碳源驱动", fill=T.AMBER_L, color="#9A5A12", size=9.5,
            pad_x=9, pad_y=4.5)
    nodes = [
        (150, NH4(color=T.AMBER, suffix="-N"), "氨氮（污染底物）", T.AMBER),
        (352, NO2(color=T.RED, suffix="-N"), "亚硝酸盐（中间态）", T.RED),
        (554, NO3(color=T.GREEN, suffix="-N"), "硝酸盐（稳定态）", T.GREEN),
        (756, N2(color=T.NAVY_L, suffix="↑"), "氮气（无害逸出）", T.NAVY_L),
    ]
    ny = 200
    for cx, formula, label, col in nodes:
        cv.rect(cx - 66, ny - 30, 132, 60, fill="FFFFFF", line=col, lw=1.6, radius=12,
                shadow=True)
        cv.rect(cx - 66, ny - 30, 132, 5, fill=col, radius=2.5)
        cv.text(cx - 62, ny - 25, 124, 26, [rich(*formula, size=16, bold=True,
                                                 color=col, align="c", spacing=1.0)],
                valign="m")
        cv.text(cx - 66, ny + 6, 132, 16, [para(text=label, size=8.5, color=T.GRAY,
                                                align="c", spacing=1.0)])
    for i, lb in enumerate(["氨氧化", "硝化", "好氧反硝化"]):
        x1 = nodes[i][0] + 70
        x2 = nodes[i + 1][0] - 70
        cv.arrow(x1, ny, x2, ny, color=T.NAVY, lw=2.0, head=9)
        cv.text((x1 + x2) / 2 - 40, ny - 26, 80, 14,
                [para(text=lb, size=9, bold=True, color=T.NAVY, align="c", spacing=1.0)])
    cv.arrow(554, ny + 32, 554, 262, color=T.GREEN, lw=1.8, head=8)
    cv.rect(452, 264, 204, 30, fill=T.GREEN_L, line=T.GREEN, lw=1.0, radius=15)
    cv.text(452, 264, 204, 30, [para(text="转化为稳定硝酸盐 · 保留堆体（保氮）", size=9.5,
                                     bold=True, color=T.GREEN, align="c", spacing=1.0)],
            valign="m")
    cards = [
        ("特性", icon_target, T.NAVY,
         [rich(("打破了氧气限制，能够在", {}), ("一个好氧体系内", {"bold": True,
               "color": T.NAVY}), ("，利用有机碳源，同步完成“氨氧化 → 亚硝酸盐/硝酸盐 → "
               "氮气”的全过程。", {}), size=11, spacing=1.36)]),
        ("应用契合度", icon_wind, T.TEAL_D,
         [rich(("完美契合堆肥的", {}), ("强制通风环境", {"bold": True, "color": T.TEAL_D}),
               ("。", {}), size=11, spacing=1.36)]),
        ("终极目标", icon_leaf, T.GREEN,
         [rich(("利用此类好氧菌，将易挥发发臭的氨氮，转化为", {}),
               ("无害的氮气排出", {"bold": True, "color": T.NAVY_L}), ("，或转化为", {}),
               ("稳定的硝酸盐保留在堆体中（保氮）", {"bold": True, "color": T.GREEN}),
               ("。", {}), size=11, spacing=1.36)]),
    ]
    for i, (ttl, icon, col, ps) in enumerate(cards):
        x = 48 + i * 294
        cv.card(x, 322, 276, 148, fill=T.WHITE, line=T.LINE, radius=12, bar=col, bar_w=4)
        cv.rect(x + 216, 336, 44, 44, fill=T.BG_SOFT2, line=None, radius=12)
        icon(cv, x + 238, 358, 26, col)
        cv.text(x + 20, 340, 190, 22, [para(text=ttl, size=14, bold=True, color=T.INK,
                                            spacing=1.0)])
        cv.line(x + 20, 368, x + 256, 368, color=T.LINE, lw=0.75)
        cv.text(x + 20, 376, 238, 84, ps, valign="m")


# ================================================================== 6 漏斗筛选
def s_funnel(cv: Canvas):
    page(cv, "PART 02 · 当前试验流程与进展", "整体研究策略 —— 漏斗式降维筛选法", 6)
    stages = [
        ("第一阶段", "初筛与富集", "121 株候选菌", "已完成", T.GREEN, T.NAVY, 360, 292,
         "利用高氨氮胁迫（好氧摇床环境），成功获得 121 株高效耐受型好氧单菌株。",
         "121 株"),
        ("第二阶段", "复筛与动力学评估", "72h 动力学 · Top 3", "正在进行 · 本阶段重点",
         T.AMBER, T.TEAL, 292, 228,
         "开展 72h 动态除氮实验，锁定转化路径，精选 Top 3 核心菌株。", "Top 3"),
        ("第三阶段", "机制解析", "基因组 + 酶活", "规划中", T.GRAY, "#4E86B8", 228, 168,
         "全基因组测序 + 关键酶活性测定。", ""),
        ("第四阶段", "堆肥实景验证", "微型反应器", "规划中", T.GRAY, "#8FB3CE", 168, 116,
         "构建合成菌群，进行微型反应器堆肥减排验证。", ""),
    ]
    cx = 228
    y = 116
    seg_h, gap = 78, 10
    for i, (sn, ttl, sub, status, scol, fill, wt, wb, desc, big) in enumerate(stages):
        pts = [(cx - wt / 2, y), (cx + wt / 2, y), (cx + wb / 2, y + seg_h),
               (cx - wb / 2, y + seg_h)]
        cv.poly(pts, fill=fill, line=None, close=True, shadow=(i == 1))
        if i == 1:
            cv.poly([(cx - wt / 2 - 5, y - 5), (cx + wt / 2 + 5, y - 5),
                     (cx + wb / 2 + 5, y + seg_h + 5), (cx - wb / 2 - 5, y + seg_h + 5)],
                    fill=None, line=T.TEAL, lw=1.6, close=True)
        if i < 2:
            cv.text(cx - 140, y + 18, 280, 20,
                    [para(text=f"{sn} · {ttl}", size=11.5, bold=True, color="FFFFFF",
                          align="c", spacing=1.0)])
            cv.text(cx - 140, y + 42, 280, 16,
                    [para(text=sub, size=8.5, color="DCE8F2", align="c", spacing=1.0)])
        else:
            cv.text(cx - 90, y + 14, 180, 18,
                    [para(text=sn, size=10, bold=True, color="FFFFFF", align="c",
                          spacing=1.0)])
            cv.text(cx - 90, y + 32, 180, 18,
                    [para(text=ttl, size=10, bold=True, color="FFFFFF", align="c",
                          spacing=1.0)])
            cv.text(cx - 90, y + 52, 180, 14,
                    [para(text=sub, size=8, color="EAF1F7", align="c", spacing=1.0)])
        rx = 436
        cv.line(cx + wt / 2 + 6, y + seg_h / 2, rx - 8, y + seg_h / 2, color=T.LINE,
                lw=1.0, dash=3)
        cv.ellipse(rx - 5, y + seg_h / 2 - 3.5, 7, 7, fill=fill)
        cv.text(rx + 4, y + 8, 300, 18,
                [para(text=f"{sn}｜{ttl}", size=11.5, bold=True, color=T.NAVY,
                      spacing=1.0)])
        cw_, _ = cv.chip(rx + 4, y + 30, status,
                         fill=T.GREEN_L if scol == T.GREEN else (T.AMBER_L if scol == T.AMBER
                                                                 else T.BG_SOFT2),
                         color=scol if scol != T.GRAY else T.GRAY,
                         size=8.5, pad_x=7, pad_y=3)
        if big:
            cv.text(rx + 4 + cw_ + 10, y + 26, 120, 24,
                    [para(text=big, size=14, bold=True,
                          color=T.NAVY if i == 0 else T.TEAL_D, spacing=1.0)])
        cv.text(rx + 4, y + 50, 452, 30, [para(text=desc, size=10.5, color=T.GRAY,
                                               spacing=1.25)])
        y += seg_h + gap
    cv.text(48, 468, 420, 16, [para(text="筛选逻辑：耐受性 → 转化效率 → 机制 → 实景",
                                    size=9.5, color=T.GRAY_L, spacing=1.0)])


# ================================================================== 7 72h 动力学
def s_kinetics(cv: Canvas):
    page(cv, "PART 02 · 当前试验流程与进展",
         "当前阶段核心实验 —— 72h 氮素转化动力学评估", 7)
    cv.card(48, 108, 864, 56, fill=T.BG_SOFT, line=T.LINE, radius=10, shadow=False,
            bar=T.NAVY, bar_w=4)
    cv.text(70, 108, 820, 56, [rich(("实验目的　", {"bold": True, "color": T.NAVY}),
                                    ("对初筛获得的候选菌株进行严格的", {}),
                                    ("氮素物料平衡（Mass Balance）", {"bold": True,
                                     "color": T.NAVY}),
                                    ("测算，探明氨氮去向。", {}), size=12.5,
                                    spacing=1.2)], valign="m")
    cards = [
        ("培养基", "HNM", icon_flask, T.NAVY,
         [rich(("采用国际标准", {}), ("异养硝化培养基（HNM）", {"bold": True, "color": T.NAVY}),
               ("，", {}), ("丁二酸钠为唯一碳源", {"bold": True, "color": T.NAVY}),
               ("，排除有机氮干扰。", {}), size=11, bullet="•", bullet_color=T.NAVY,
               spacing=1.34)]),
        ("接种标准", "OD600 = 0.1", icon_drop, T.TEAL_D,
         [rich(("全样本采用“", {}), ("对数期洗菌纯化", {"bold": True, "color": T.TEAL_D}),
               ("”。", {}), size=11, bullet="•", bullet_color=T.TEAL_D, spacing=1.34,
               space_after=4),
          rich(("统一初始接种量（", {}), ("OD", {"bold": True, "color": T.TEAL_D}),
               ("600", {"sub": True, "bold": True, "color": T.TEAL_D}),
               ("=0.1", {"bold": True, "color": T.TEAL_D}),
               ("），确保起跑线一致。", {}), size=11, bullet="•", bullet_color=T.TEAL_D,
               spacing=1.34)]),
        ("培养环境", "30℃ / 150 rpm", icon_temp, T.AMBER,
         [rich(("30℃", {"bold": True, "color": T.AMBER}), ("，", {}),
               ("150 rpm 高转速", {"bold": True, "color": T.AMBER}),
               ("好氧培养。", {}), size=11, bullet="•", bullet_color=T.AMBER,
               spacing=1.34)]),
    ]
    for i, (ttl, tag, icon, col, ps) in enumerate(cards):
        x = 48 + i * 294
        cv.card(x, 178, 276, 124, fill=T.WHITE, line=T.LINE, radius=12, bar=col, bar_w=4)
        cv.rect(x + 216, 190, 44, 44, fill=T.BG_SOFT2, line=None, radius=12)
        icon(cv, x + 238, 212, 26, col)
        cv.text(x + 20, 192, 150, 22, [para(text="培养体系 · " + ttl, size=13, bold=True,
                                            color=T.INK, spacing=1.0)])
        cv.chip(x + 20, 220, tag, fill=T.BG_SOFT2, color=col, size=9, pad_x=8, pad_y=3.5)
        cv.text(x + 20, 246, 240, 52, ps)
    # Mass balance 框架
    cv.card(48, 310, 864, 182, fill=T.WHITE, line=T.LINE, radius=14)
    cv.text(68, 322, 400, 18, [para(text="氮素物料平衡（Mass Balance）测算框架",
                                    size=11.5, bold=True, color=T.NAVY, spacing=1.0)])
    cv.text(680, 322, 212, 18, [para(text="探明氨氮去向：气态 / 液相 / 生物量",
                                     size=9.5, color=T.GRAY, align="r", spacing=1.0)])
    bx, by, bw, bh = 76, 366, 158, 92
    cv.rect(bx, by, bw, bh, fill=T.AMBER_L, line=T.AMBER, lw=1.4, radius=10)
    cv.text(bx, by + 16, bw, 24, [rich(*NH4(color=T.AMBER, suffix="-N"), size=15,
                                       bold=True, align="c", spacing=1.0)], valign="m")
    cv.text(bx, by + 44, bw, 16, [para(text="初始氨氮投入", size=9.5, color=T.GRAY,
                                       align="c", spacing=1.0)])
    cv.text(bx, by + 62, bw, 16, [para(text="（t = 0 h）", size=9, color=T.GRAY_L,
                                       align="c", spacing=1.0)])
    jx, jy = 292, by + bh / 2
    cv.line(bx + bw, jy, jx, jy, color=T.GRAY_L, lw=1.6)
    cv.ellipse(jx - 4, jy - 4, 8, 8, fill=T.GRAY_L)
    outs = [
        (T.NAVY_L, "生物量氮",
         [para(text="细胞同化 · 菌体干重 / OD600 表征", size=9.5, color=T.GRAY,
               spacing=1.15)]),
        (T.GREEN, "液相残留氮",
         [rich(("NO", {}), ("2", {"sub": True}), ("-", {"sup": True}), ("-N / NO", {}),
               ("3", {"sub": True}), ("-", {"sup": True}),
               ("-N 残留（保氮）", {}), size=9.5, color=T.GRAY, spacing=1.15)]),
        (T.RED, "气态氮损失",
         [rich(("N", {}), ("2", {"sub": True}),
               ("↑ 逸出 · 证实好氧反硝化产气", {}), size=9.5, color=T.GRAY,
               spacing=1.15)]),
    ]
    for k, (col, ttl, sub) in enumerate(outs):
        oy = 340 + k * 52
        cv.arrow(jx + 4, jy, 470, oy + 21, color=col, lw=1.6, head=8)
        cv.rect(478, oy, 414, 42, fill=T.WHITE, line=col, lw=1.4, radius=10)
        cv.rect(478, oy, 5, 42, fill=col, radius=2.5)
        cv.text(496, oy, 130, 42, [para(text=ttl, size=12, bold=True, color=col,
                                        spacing=1.0)], valign="m")
        cv.line(630, oy + 8, 630, oy + 34, color=T.LINE, lw=0.75)
        cv.text(644, oy, 240, 42, sub, valign="m")


# ================================================================== 8 取样与指标
def s_metrics(cv: Canvas):
    page(cv, "PART 02 · 当前试验流程与进展", "取样与核心检测指标体系", 8)
    cv.card(48, 108, 864, 104, fill=T.WHITE, line=T.LINE, radius=14)
    cv.text(68, 120, 260, 18, [para(text="动态取样频次 · 无菌操作", size=11.5, bold=True,
                                    color=T.NAVY, spacing=1.0)])
    cv.text(250, 122, 420, 16, [para(text="第 0、12、24、36、48、60、72 小时无菌取样",
                                     size=10, color=T.GRAY, spacing=1.0)])
    cv.chip(760, 118, "检测方法：国标法", fill=T.BG_SOFT2, color=T.NAVY, size=9.5,
            pad_x=9, pad_y=4.5)
    hours = [0, 12, 24, 36, 48, 60, 72]
    x0, x1 = 108, 852
    yline = 176
    cv.line(x0, yline, x1, yline, color=T.LINE, lw=2.0)
    for i, h in enumerate(hours):
        x = x0 + (x1 - x0) * i / 6
        cv.ellipse(x - 11, yline - 11, 22, 22,
                   fill=T.NAVY if h not in (0, 72) else T.TEAL, line="FFFFFF", lw=2)
        cv.text(x - 16, yline - 11, 32, 22, [para(text=str(h), size=9.5, bold=True,
                                                  color="FFFFFF", align="c",
                                                  spacing=1.0)], valign="m")
    cv.text(x1 - 4, yline + 14, 30, 14, [para(text="t / h", size=8.5, color=T.GRAY,
                                              spacing=1.0)])
    cv.arrow(x1 + 8, yline, x1 + 26, yline, color=T.TEAL, lw=2.0, head=8)
    metrics = [
        (NH4(color=T.AMBER, suffix="-N"), "氨氮", T.AMBER,
         "评估初始污染物的直接降解能力。", "降解能力"),
        (NO2(color=T.RED, suffix="-N"), "亚硝酸盐氮", T.RED,
         "监测是否有毒性中间产物积累。", "一票否决指标"),
        (NO3(color=T.GREEN, suffix="-N"), "硝酸盐氮", T.GREEN,
         "评估菌株将游离氨转化为稳定固态氮肥的能力（保氮指标）。", "保氮"),
        ([("TN", {"color": T.BLUE})], "总氮", T.BLUE,
         "结合细胞干重（或OD600），计算气态氮流失率，证实好氧反硝化产气能力。",
         "气态流失率"),
    ]
    for i, (formula, name, col, desc, tag) in enumerate(metrics):
        x = 48 + i * 220
        cv.card(x, 228, 204, 176, fill=T.WHITE, line=T.LINE, radius=12)
        cv.rect(x, 228, 204, 6, fill=col, radius=3)
        cv.rect(x + 14, 248, 40, 40, fill=T.BG_SOFT2, line=None, radius=10)
        cv.text(x + 14, 248, 40, 40, [para(text=str(i + 1), size=15, bold=True,
                                           color=col, align="c", spacing=1.0)],
                valign="m")
        cv.text(x + 64, 248, 130, 24, [rich(*formula, size=15, bold=True, color=col,
                                             spacing=1.0)], valign="m")
        cv.text(x + 64, 272, 130, 16, [para(text=name, size=10, bold=True, color=T.INK,
                                            spacing=1.0)])
        cv.line(x + 14, 298, x + 190, 298, color=T.LINE, lw=0.75)
        cv.text(x + 14, 308, 176, 68, [para(text=desc, size=10, color=T.GRAY,
                                            spacing=1.35)])
        cv.chip(x + 14, 360, tag, fill=(T.RED_L if i == 1 else T.BG_SOFT2),
                color=col, size=8.5, pad_x=8, pad_y=3.5)
    cv.card(48, 420, 864, 44, fill=T.BG_SOFT, line=T.LINE, radius=10, shadow=False,
            bar=T.NAVY, bar_w=4)
    cv.text(70, 420, 820, 44, [rich(("指标逻辑：", {"bold": True, "color": T.NAVY}),
                                    ("降解（NH", {}), ("4", {"sub": True}),
                                    ("+）→ 安全（NO", {}), ("2", {"sub": True}),
                                    ("- 不积累）→ 保氮（NO", {}), ("3", {"sub": True}),
                                    ("- 生成）→ 归趋（TN 平衡）", {}),
                                    size=10.5, color=T.GRAY, spacing=1.1)], valign="m")


# ================================================================== 9 预期与计划
def s_plan(cv: Canvas):
    page(cv, "PART 02 · 当前试验流程与进展", "预期结果与下一步计划", 9)
    cv.card(48, 108, 486, 376, fill=T.WHITE, line=T.LINE, radius=14)
    cv.text(68, 124, 300, 20, [para(text="预期输出成果", size=14, bold=True, color=T.NAVY,
                                    spacing=1.0)])
    cv.rect(68, 148, 34, 3, fill=T.TEAL)
    cv.text(68, 160, 446, 76, [
        rich(("绘制出目标菌株的“生长-降氮”特征动力学曲线。", {}), size=11.5,
             bullet="•", bullet_color=T.TEAL, spacing=1.32, space_after=5),
        rich(("从 121 株菌中，精准锁定 1-2 株具备“", {}),
             ("不积累亚硝酸盐 + 总氮显著下降/转化为硝态氮", {"bold": True,
              "color": T.TEAL_D}), ("”的王牌好氧降氨菌。", {}), size=11.5, bullet="•",
             bullet_color=T.TEAL, spacing=1.32)])
    gx, gy, gw, gh = 92, 282, 396, 156
    cv.rect(gx, gy, gw, gh, fill=T.BG_SOFT, line=None, radius=8)
    curves = [
        ([(0, 0.92), (0.25, 0.55), (0.5, 0.22), (0.75, 0.12), (1, 0.08)], T.AMBER,
         "NH4+-N"),
        ([(0, 0.10), (0.3, 0.34), (0.6, 0.62), (1, 0.80)], T.GREEN, "NO3--N"),
        ([(0, 0.86), (0.35, 0.66), (0.7, 0.46), (1, 0.36)], T.BLUE, "TN"),
        ([(0, 0.06), (0.3, 0.42), (0.6, 0.66), (0.85, 0.74), (1, 0.76)], T.NAVY,
         "OD600"),
    ]
    for i, (pts, col, lb) in enumerate(curves):
        xx = gx + 46 + i * 92
        cv.line(xx, gy + 12, xx + 16, gy + 12, color=col, lw=2.2)
        cv.text(xx + 20, gy + 5, 76, 14, [para(text=lb, size=8, bold=True, color=col,
                                               spacing=1.0)])
    ax0, ay0 = gx + 34, gy + gh - 24
    cv.line(ax0, gy + 26, ax0, ay0, color=T.GRAY_L, lw=1.2)
    cv.line(ax0, ay0, gx + gw - 14, ay0, color=T.GRAY_L, lw=1.2)
    cv.arrow(ax0, gy + 26, ax0, gy + 20, color=T.GRAY_L, lw=1.2, head=6)
    cv.arrow(gx + gw - 14, ay0, gx + gw - 6, ay0, color=T.GRAY_L, lw=1.2, head=6)
    cv.text(gx + 40, gy + 22, 120, 14, [para(text="浓度 / OD600", size=8, color=T.GRAY_L,
                                             spacing=1.0)])
    cv.text(gx + gw - 60, gy + gh - 18, 50, 14, [para(text="t / h", size=8,
                                                      color=T.GRAY_L, spacing=1.0)])
    for i, h in enumerate((0, 24, 48, 72)):
        xx = ax0 + (gw - 60) * i / 3
        cv.line(xx, ay0, xx, ay0 + 4, color=T.GRAY_L, lw=1)
        cv.text(xx - 10, ay0 + 6, 24, 12, [para(text=str(h), size=7.5, color=T.GRAY_L,
                                                align="c", spacing=1.0)])
    for pts, col, lb in curves:
        cpts = [(ax0 + 6 + (gw - 66) * t, ay0 - 8 - v * (gh - 66)) for t, v in pts]
        cv.curve(cpts, color=col, lw=2.0)
    cv.text(gx, gy + gh + 6, gw, 14, [para(text="示意图：预期“生长-降氮”动力学趋势（非实测数据）",
                                          size=8.5, color=T.GRAY_L, align="c",
                                          spacing=1.0)])
    cv.card(558, 108, 354, 376, fill=T.WHITE, line=T.LINE, radius=14)
    cv.text(578, 124, 300, 20, [para(text="近期下一步工作", size=14, bold=True,
                                     color=T.NAVY, spacing=1.0)])
    cv.rect(578, 148, 34, 3, fill=T.TEAL)
    steps = [
        ("STEP 1", "16S rRNA 种属鉴定",
         "对选定的王牌菌株进行 16S rRNA 种属鉴定。", icon_target, T.NAVY),
        ("STEP 2", "全基因组测序",
         "提取 DNA 送检全基因组测序。", icon_dna, T.TEAL_D),
        ("STEP 3", "酶系验证前期准备",
         "为后续的氨氧化酶系（AMO）和反硝化酶系（NIR/NAR）验证做前期准备。",
         icon_flask, T.GREEN),
    ]
    yy = 172
    for i, (tag, ttl, desc, icon, col) in enumerate(steps):
        cv.rect(578, yy, 314, 88, fill=T.BG_SOFT, line=None, radius=10)
        cv.rect(578, yy, 4, 88, fill=col, radius=2)
        cv.badge(606, yy + 26, 30, str(i + 1), fill=col, color="FFFFFF", size=13)
        cv.text(628, yy + 10, 200, 18, [para(text=tag, size=8.5, bold=True, color=col,
                                             spacing=1.0)])
        cv.text(628, yy + 26, 250, 20, [para(text=ttl, size=12.5, bold=True, color=T.INK,
                                             spacing=1.0)])
        cv.text(600, yy + 52, 280, 32, [para(text=desc, size=9.5, color=T.GRAY,
                                             spacing=1.3)])
        icon(cv, 866, yy + 30, 26, col)
        if i < 2:
            cv.arrow(594, yy + 92, 594, yy + 104, color=T.GRAY_L, lw=1.4, head=7)
        yy += 104


# ================================================================== 10 尾页
def s_thanks(cv: Canvas):
    cv.bg = None
    cv.rect(0, 0, 960, 540, grad=(T.NAVY_D, "#10497E", 90))
    cv.ellipse(-190, 240, 480, 480, line="FFFFFF", lw=1.0, alpha=0.08)
    cv.ellipse(-124, 306, 348, 348, line=T.TEAL, lw=1.2, alpha=0.30)
    cv.ellipse(760, -160, 420, 420, line="FFFFFF", lw=0.9, alpha=0.10)
    cv.rect(0, 0, 7, 540, grad=(T.TEAL, T.TEAL_D, 90))
    cv.text(120, 176, 720, 60, [para(text="感谢各位老师和同学的聆听！", size=33, bold=True,
                                     color="FFFFFF", align="c", spacing=1.2)])
    cv.text(120, 244, 720, 30, [para(text="敬请批评指正。", size=17, color="9FD8CE",
                                     align="c", spacing=1.2)])
    cv.rect(436, 296, 88, 4, fill=T.TEAL)
    cv.text(120, 330, 720, 20, [para(text="高效好氧降氨菌的筛选、机制解析及其在堆肥减排保氮中的应用",
                                     size=11, color="B9CBDD", align="c", spacing=1.2)])
    cv.text(120, 356, 720, 18, [para(text="汇报人：[你的名字]　|　指导教师：[导师名字]　|　202X年X月X日",
                                     size=10.5, color="8FA6BD", align="c", spacing=1.2)])
    logo(cv, dark=True)
    cv.chip(408, 420, "HN-AD · 好氧降氨菌", fill=T.TEAL, color="FFFFFF", size=10,
            pad_x=12, pad_y=6)


ALL = [s_cover, s_toc, s_bg, s_paradox, s_hnad, s_funnel, s_kinetics, s_metrics,
       s_plan, s_thanks]
NAMES = ["cover", "toc", "01-background", "02-paradox", "03-hnad", "04-funnel",
         "05-kinetics", "06-metrics", "07-plan", "thanks"]
