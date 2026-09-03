# -*- coding: utf-8 -*-
"""
deckkit.layout —— 版式引擎（单位：pt，1pt = 1/72 in，画布 960 x 540）

设计要点：所有排版计算（换行、行高、对齐、缩进、居中）都在这里完成，
PPTX 与 PNG 两个渲染器只负责"照着画"，因此预览与最终文件版式一致。
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import ImageFont

from . import theme as T

HERE = os.path.dirname(os.path.abspath(__file__))
PT2EMU = 12700

# ---------------------------------------------------------------- 字体度量

_FONT_CACHE: Dict[Tuple[int, bool], ImageFont.FreeTypeFont] = {}
_METRIC_SCALE = 8          # 以 8 倍字号测量，得到亚像素精度
_warnings: List[str] = []


def _preview_font(size_pt: float, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = (int(round(size_pt * _METRIC_SCALE)), bold)
    f = _FONT_CACHE.get(key)
    if f is None:
        path = os.path.join(HERE, T.F_PREVIEW)
        f = ImageFont.truetype(path, size=max(1, key[0]))
        _FONT_CACHE[key] = f
    return f


def text_width(s: str, size: float, bold: bool = False) -> float:
    """文本宽度（pt）。用 Droid Sans Fallback 作度量代理，略宽于 微软雅黑/Arial，偏保守。"""
    if not s:
        return 0.0
    f = _preview_font(size, bold)
    w = f.getlength(s) / _METRIC_SCALE
    return w * (1.035 if bold else 1.0)


# 简易避头尾
_NO_START = set("）)，。、；：？！%‰》」』】〉〕" + ".,;:?!%)]}")
_NO_END = set("（《「『【〈〔" + "([{")


def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE4F
            or 0xFF00 <= o <= 0xFFEF or 0x3000 <= o <= 0x303F or 0x20000 <= o <= 0x2FA1F)


def _tokenize(text: str, ri: int) -> List[Dict[str, Any]]:
    """把一段文字切成原子：CJK 单字 / 西文词 / 空格。"""
    atoms: List[Dict[str, Any]] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == " ":
            atoms.append({"t": " ", "ri": ri, "space": True})
            i += 1
        elif ch == "\t":
            atoms.append({"t": "  ", "ri": ri, "space": True})
            i += 1
        elif _is_cjk(ch):
            atoms.append({"t": ch, "ri": ri})
            i += 1
        else:
            j = i
            while j < n and text[j] != " " and not _is_cjk(text[j]):
                # 允许在 - / ~ 后断行（西文长词）；并限制原子长度，避免超宽不可断
                if j > i and text[j - 1] in "-/~":
                    break
                if j - i >= 26:
                    break
                j += 1
            atoms.append({"t": text[i:j], "ri": ri})
            i = j
    return atoms


# ---------------------------------------------------------------- 数据结构

@dataclass
class Run:
    text: str
    size: float = 12.0
    bold: bool = False
    color: str = T.INK
    italic: bool = False
    baseline: float = 0.0        # 0 正常 / -0.25 下标 / 0.3 上标
    font_ea: str = T.F_EA
    font_latin: str = T.F_LATIN
    spacing: float = 0.0         # 字间距 pt


@dataclass
class Para:
    runs: List[Run] = field(default_factory=list)
    align: str = "l"             # l / c / r / j
    spacing: float = 1.22        # 行距倍数
    space_before: float = 0.0
    space_after: float = 0.0
    bullet: Optional[str] = None  # '•' '–' '▪' '✓' ...
    bullet_color: Optional[str] = None
    indent: float = 0.0          # 首行/整体缩进
    bullet_gap: float = 14.0


@dataclass
class LayoutLine:
    x: float
    y: float
    h: float
    runs: List[Run]
    align: str
    bullet: Optional[str] = None
    bullet_color: str = T.GRAY
    bullet_x: float = 0.0
    bullet_size: float = 12.0
    width: float = 0.0


def para(text=None, runs=None, size=12.0, bold=False, color=T.INK, align="l",
         spacing=1.22, space_before=0.0, space_after=0.0, bullet=None,
         bullet_color=None, indent=0.0, italic=False, **kw) -> Para:
    """便捷构造段落。runs 可为 [(text, {size/bold/color/baseline}), ...]"""
    if runs is None:
        runs = [Run(text=text or "", size=size, bold=bold, color=color, italic=italic)]
    else:
        rr = []
        for item in runs:
            if isinstance(item, str):
                rr.append(Run(text=item, size=size, bold=bold, color=color))
            elif isinstance(item, Run):
                rr.append(item)
            else:
                t, st = item
                rr.append(Run(text=t, size=st.get("size", size), bold=st.get("bold", bold),
                              color=st.get("color", color), italic=st.get("italic", italic),
                              baseline=st.get("baseline", 0.0)))
        runs = rr
    return Para(runs=runs, align=align, spacing=spacing, space_before=space_before,
                space_after=space_after, bullet=bullet, bullet_color=bullet_color,
                indent=indent, **kw)


def rich(*parts, size=12.0, bold=False, color=T.INK, **kw) -> Para:
    """rich(('NH',{}),('4',{sub}),('+',{sup})) 形式的化学式段落"""
    runs = []
    for p in parts:
        if isinstance(p, str):
            runs.append(Run(text=p, size=size, bold=bold, color=color))
        else:
            t, st = p
            s = st.get("size", size)
            base = 0.0
            if st.get("sub"):
                base, s = -0.24, size * 0.70
            if st.get("sup"):
                base, s = 0.30, size * 0.70
            runs.append(Run(text=t, size=s, bold=st.get("bold", bold),
                            color=st.get("color", color), baseline=base,
                            italic=st.get("italic", False)))
    return Para(runs=runs, align=kw.get("align", "l"), spacing=kw.get("spacing", 1.22),
                space_before=kw.get("space_before", 0.0), space_after=kw.get("space_after", 0.0),
                bullet=kw.get("bullet"), bullet_color=kw.get("bullet_color"),
                indent=kw.get("indent", 0.0))


# ---------------------------------------------------------------- 排版计算

def layout_paras(paras: Sequence[Para], x: float, y: float, w: float,
                 valign: str = "t", h: Optional[float] = None) -> Tuple[List[LayoutLine], float]:
    """把段落排成一行行绝对定位的 LayoutLine。返回 (lines, total_height)。"""
    blocks: List[LayoutLine] = []
    total = 0.0
    for p in paras:
        marL = p.indent + (p.bullet_gap if p.bullet else 0.0)
        avail = max(20.0, w - marL)
        atoms: List[Tuple[Dict[str, Any], Run]] = []
        for ri, r in enumerate(p.runs):
            for a in _tokenize(r.text, ri):
                atoms.append((a, r))
        # 逐原子量宽
        widths = []
        for a, r in atoms:
            widths.append(text_width(a["t"], r.size, r.bold))
        # 贪心换行
        lines: List[List[int]] = []
        cur: List[int] = []
        curw = 0.0
        for idx, ((a, r), aw) in enumerate(zip(atoms, widths)):
            if cur and curw + aw > avail and not a.get("space"):
                # 避头尾：下一原子不能行首 -> 把上一原子挪到下一行
                if a["t"] and a["t"][0] in _NO_START and len(cur) > 1:
                    moved = cur.pop()
                    lines.append(cur)
                    cur = [moved, idx]
                    curw = widths[moved] + aw
                    continue
                lines.append(cur)
                cur = [idx]
                curw = aw
            elif cur and a.get("space") and curw + aw > avail:
                lines.append(cur)
                cur = []
                curw = 0.0
            else:
                cur.append(idx)
                curw += aw
        if cur:
            lines.append(cur)
        if not lines:
            lines = [[]]

        psize = max([r.size for r in p.runs] or [12.0])
        lh = psize * p.spacing
        total += p.space_before
        for li, idxs in enumerate(lines):
            # 去掉行尾空格
            while idxs and atoms[idxs[-1]][0].get("space"):
                idxs.pop()
            lw = sum(widths[i] for i in idxs)
            if p.align == "c":
                lx = x + marL + max(0.0, (avail - lw) / 2.0)
            elif p.align == "r":
                lx = x + marL + max(0.0, avail - lw)
            else:
                lx = x + marL
            # 合并同 run 的连续原子
            merged: List[Run] = []
            for i in idxs:
                a, r = atoms[i]
                if merged and merged[-1] is r:
                    merged[-1] = Run(text=merged[-1].text + a["t"], size=r.size, bold=r.bold,
                                     color=r.color, italic=r.italic, baseline=r.baseline,
                                     font_ea=r.font_ea, font_latin=r.font_latin,
                                     spacing=r.spacing)
                else:
                    merged.append(Run(text=a["t"], size=r.size, bold=r.bold, color=r.color,
                                      italic=r.italic, baseline=r.baseline,
                                      font_ea=r.font_ea, font_latin=r.font_latin,
                                      spacing=r.spacing))
            first = (li == 0)
            blocks.append(LayoutLine(
                x=lx, y=y + total + (p.space_before if first else 0.0), h=lh,
                runs=merged, align=p.align,
                bullet=(p.bullet if first else None),
                bullet_color=(p.bullet_color or T.GRAY),
                bullet_x=x + p.indent, bullet_size=psize, width=lw))
            total += lh
        total += p.space_after
    # 垂直对齐
    if h is not None and valign in ("m", "b"):
        extra = max(0.0, h - total)
        dy = extra / 2.0 if valign == "m" else extra
        if dy:
            for b in blocks:
                b.y += dy
    return blocks, total


# ---------------------------------------------------------------- 画布

class Canvas:
    """记录绘制指令；由 to_pptx / to_png 渲染。"""

    def __init__(self, name: str = "", bg: str = T.WHITE, w: float = T.SLIDE_W,
                 h: float = T.SLIDE_H):
        self.name = name
        self.bg = bg
        self.w = w
        self.h = h
        self.items: List[Dict[str, Any]] = []

    # ---- 基础图元
    def rect(self, x, y, w, h, fill=None, line=None, lw=0.75, radius=0.0,
             shadow=False, alpha=None, dash=None, grad=None):
        self.items.append(dict(kind="rect", x=x, y=y, w=w, h=h, fill=fill, line=line,
                               lw=lw, radius=radius, shadow=shadow, alpha=alpha,
                               dash=dash, grad=grad))

    def ellipse(self, x, y, w, h, fill=None, line=None, lw=0.75, shadow=False,
                alpha=None, dash=None):
        self.items.append(dict(kind="ellipse", x=x, y=y, w=w, h=h, fill=fill, line=line,
                               lw=lw, shadow=shadow, alpha=alpha, dash=dash))

    def poly(self, pts, fill=None, line=None, lw=0.75, close=True, shadow=False, alpha=None):
        self.items.append(dict(kind="poly", pts=list(pts), fill=fill, line=line, lw=lw,
                               close=close, shadow=shadow, alpha=alpha))

    def path(self, pts, line=None, lw=1.5, fill=None, close=False, dash=None,
             cap="rnd", alpha=None):
        self.items.append(dict(kind="path", pts=list(pts), line=line, lw=lw, fill=fill,
                               close=close, dash=dash, cap=cap, alpha=alpha))

    def line(self, x1, y1, x2, y2, color=T.LINE, lw=1.0, dash=None, cap="flat",
             alpha=None):
        self.items.append(dict(kind="line", pts=[(x1, y1), (x2, y2)], line=color, lw=lw,
                               fill=None, close=False, dash=dash, cap=cap, alpha=alpha))

    def arrow(self, x1, y1, x2, y2, color=T.GRAY, lw=1.8, head=9.0, dash=None,
              shorten=0.0):
        """带三角箭头的直线（箭头单独画，PPTX/PNG 表现一致）"""
        ang = math.atan2(y2 - y1, x2 - x1)
        if shorten:
            x2 -= math.cos(ang) * shorten
            y2 -= math.sin(ang) * shorten
        bx = x2 - math.cos(ang) * head * 0.92
        by = y2 - math.sin(ang) * head * 0.92
        self.line(x1, y1, bx, by, color=color, lw=lw, dash=dash, cap="rnd")
        hw = head * 0.46
        p1 = (x2, y2)
        p2 = (bx - math.sin(ang) * hw, by + math.cos(ang) * hw)
        p3 = (bx + math.sin(ang) * hw, by - math.cos(ang) * hw)
        self.poly([p1, p2, p3], fill=color, line=None, close=True)

    def curve(self, pts, color=T.NAVY, lw=2.0, fill=None, close=False, dash=None,
              samples=16, tension=0.5):
        """Catmull-Rom 平滑曲线 -> 密集折线"""
        self.path(catmull_rom(pts, samples=samples, tension=tension), line=color, lw=lw,
                  fill=fill, close=close, dash=dash)

    # ---- 文本
    def text(self, x, y, w, h=None, paras=(), valign="t", name=""):
        if isinstance(paras, (Para, dict, str)):
            paras = [paras]
        ps = []
        for p in paras:
            if isinstance(p, str):
                ps.append(para(text=p))
            elif isinstance(p, dict):
                ps.append(para(**p))
            else:
                ps.append(p)
        lines, total = layout_paras(ps, x, y, w, valign=valign, h=h)
        if h is not None and total > h + 1.5:
            _warnings.append(f"[{self.name}] 文本溢出 {total:.1f}pt > {h:.1f}pt  @({x:.0f},{y:.0f}) "
                             f"{ps[0].runs[0].text[:18] if ps and ps[0].runs else ''}")
        self.items.append(dict(kind="text", x=x, y=y, w=w, h=(h if h is not None else total),
                               lines=lines, paras=ps, valign=valign))
        return total

    # ---- 组合便捷件
    def card(self, x, y, w, h, fill=T.WHITE, line=T.LINE, lw=0.75, radius=10.0,
             shadow=True, bar=None, bar_w=4.0):
        self.rect(x, y, w, h, fill=fill, line=line, lw=lw, radius=radius, shadow=shadow)
        if bar:
            self.rect(x, y + (radius * 0.35 if radius else 0), bar_w,
                      h - (radius * 0.7 if radius else 0), fill=bar, line=None,
                      radius=bar_w / 2.0)

    def chip(self, x, y, text_, fill=T.TEAL_L, color=T.TEAL_D, size=10.0, pad_x=9.0,
             pad_y=4.5, bold=True, h=None, radius=None):
        w = text_width(text_, size, bold) + pad_x * 2
        hh = h or (size * 1.25 + pad_y * 2)
        r = hh / 2.0 if radius is None else radius
        self.rect(x, y, w, hh, fill=fill, line=None, radius=r)
        self.text(x, y, w, hh, [para(text=text_, size=size, bold=bold, color=color,
                                     align="c", spacing=1.0)], valign="m")
        return w, hh

    def badge(self, cx, cy, d, text_, fill=T.NAVY, color=T.WHITE, size=12.0,
              line=None, lw=1.0, bold=True):
        self.ellipse(cx - d / 2, cy - d / 2, d, d, fill=fill, line=line, lw=lw)
        self.text(cx - d / 2, cy - d / 2, d, d,
                  [para(text=text_, size=size, bold=bold, color=color, align="c",
                        spacing=1.0)], valign="m")


def catmull_rom(pts, samples=14, tension=1.0) -> List[Tuple[float, float]]:
    """Catmull-Rom 样条 -> 密集折线。tension=1 为标准样条，0 退化为直线连接。"""
    if len(pts) < 3:
        return list(pts)
    p = [pts[0]] + list(pts) + [pts[-1]]
    out: List[Tuple[float, float]] = []

    def _at(a, b, c, d, t):
        t2, t3 = t * t, t * t * t
        smooth = 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2
                        + (-a + 3 * b - 3 * c + d) * t3)
        linear = b + (c - b) * t
        return tension * smooth + (1.0 - tension) * linear

    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for s in range(samples):
            t = s / samples
            out.append((_at(p0[0], p1[0], p2[0], p3[0], t),
                        _at(p0[1], p1[1], p2[1], p3[1], t)))
    out.append((float(pts[-1][0]), float(pts[-1][1])))
    return out


def warnings() -> List[str]:
    return list(_warnings)


def reset_warnings():
    _warnings.clear()
