# -*- coding: utf-8 -*-
"""deckkit.to_png —— 用 Pillow 把 Canvas 渲染成 PNG（1:1 还原 PPTX 版式，用于校对与预览）。"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import theme as T
from .layout import Canvas, LayoutLine, Run, text_width
from . import theme as T

_HERE = os.path.dirname(os.path.abspath(__file__))
_DF_CACHE = {}


def _dfont(size_pt: float, bold: bool, scale: float):
    """绘制用字体：像素尺寸 = pt * scale（与 _preview_font 的 8 倍度量字体区分）"""
    key = (int(round(size_pt * scale)), bold)
    f = _DF_CACHE.get(key)
    if f is None:
        f = ImageFont.truetype(os.path.join(_HERE, T.F_PREVIEW), size=max(1, key[0]))
        _DF_CACHE[key] = f
    return f


def _rgb(hexstr: str) -> Tuple[int, int, int]:
    h = hexstr.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore


def _lerp(c1, c2, t):
    a, b = _rgb(c1), _rgb(c2)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _gradient_image(w: int, h: int, c1: str, c2: str, ang_deg: float) -> Image.Image:
    """按 PowerPoint lin ang 语义生成线性渐变（0=左→右，90=上→下）"""
    strip = Image.new("RGB", (256, 1))
    for i in range(256):
        strip.putpixel((i, 0), _lerp(c1, c2, i / 255.0))
    rad = math.radians(ang_deg)
    dx, dy = math.cos(rad), math.sin(rad)
    corners = [(0, 0), (w, 0), (0, h), (w, h)]
    projs = [x * dx + y * dy for x, y in corners]
    lo, hi = min(projs), max(projs)
    span = (hi - lo) or 1.0
    k = 255.0 / span
    return strip.transform((w, h), Image.AFFINE, (dx * k, dy * k, -lo * k, 0, 0, 0.5),
                           resample=Image.BILINEAR)


class PngRenderer:
    def __init__(self, scale: float = 3.0, out_scale: float = 2.0):
        self.S = scale
        self.out = out_scale

    # ---------- 主入口
    def render(self, cv: Canvas, path: str) -> str:
        S = self.S
        W, H = int(round(cv.w * S)), int(round(cv.h * S))
        img = Image.new("RGB", (W, H), _rgb(cv.bg or T.WHITE))
        self.img = img
        self.draw = ImageDraw.Draw(img, "RGBA")
        for it in cv.items:
            getattr(self, "_" + it["kind"])(it)
        if self.out != S:
            k = self.out / S
            img = img.resize((int(round(cv.w * self.out)), int(round(cv.h * self.out))),
                             Image.LANCZOS)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        img.save(path, "PNG", optimize=True)
        return path

    # ---------- 工具
    def _shadow(self, shape_img: Image.Image, xy: Tuple[float, float],
                blur: float = 5.0, dy: float = 2.0, alpha: int = 46):
        S = self.S
        pad = int(blur * S * 2.5)
        layer = Image.new("RGBA", (shape_img.width + 2 * pad, shape_img.height + 2 * pad),
                          (0, 0, 0, 0))
        mask = shape_img.split()[-1].point(lambda v: int(v * alpha / 255))
        dark = Image.new("RGBA", shape_img.size, (10, 30, 52, 255))
        layer.paste(dark, (pad, pad), mask)
        layer = layer.filter(ImageFilter.GaussianBlur(blur * S * 0.55))
        self.img.paste(layer, (int(xy[0] * S) - pad, int((xy[1] + dy) * S) - pad), layer)
        self.draw = ImageDraw.Draw(self.img, "RGBA")

    def _shape_layer(self, painter, size, fill_rgba, shadow=False):
        """在独立 RGBA 图层上画形状（支持半透明与阴影）后合成"""
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        painter(d)
        if fill_rgba is not None and fill_rgba[3] < 255:
            alpha = fill_rgba[3]
            layer.putalpha(layer.split()[-1].point(lambda v: int(v * alpha / 255)))
        return layer

    # ---------- 图元
    def _rect(self, it: Dict[str, Any]):
        S = self.S
        x, y, w, h = it["x"] * S, it["y"] * S, it["w"] * S, it["h"] * S
        r = min(it.get("radius", 0.0) * S, min(w, h) / 2.0)
        fill = it.get("fill")
        line = it.get("line")
        lw = it.get("lw", 0.75) * S

        if it.get("shadow") and fill:
            box = Image.new("RGBA", (int(w) + 2, int(h) + 2), (0, 0, 0, 0))
            ImageDraw.Draw(box).rounded_rectangle([1, 1, w + 1, h + 1], radius=r,
                                                  fill=(255, 255, 255, 255))
            self._shadow(box, (it["x"] - 1 / S, it["y"] - 1 / S))

        if it.get("grad"):
            c1, c2, ang = it["grad"]
            gi = _gradient_image(int(w) + 2, int(h) + 2, c1, c2, ang)
            mask = Image.new("L", (int(w) + 2, int(h) + 2), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
            self.img.paste(gi, (int(x), int(y)), mask)
            self.draw = ImageDraw.Draw(self.img, "RGBA")
        elif fill:
            a = 255 if it.get("alpha") is None else int(it["alpha"] * 255)
            self.draw.rounded_rectangle([x, y, x + w, y + h], radius=r,
                                        fill=_rgb(fill) + (a,))
        if line:
            a = 255 if it.get("alpha") is None else int(it["alpha"] * 255)
            self.draw.rounded_rectangle([x + lw / 2, y + lw / 2, x + w - lw / 2,
                                         y + h - lw / 2], radius=max(0, r - lw / 2),
                                        outline=_rgb(line) + (a,), width=max(1, int(round(lw))))

    def _ellipse(self, it: Dict[str, Any]):
        S = self.S
        x, y, w, h = it["x"] * S, it["y"] * S, it["w"] * S, it["h"] * S
        lw = it.get("lw", 0.75) * S
        if it.get("shadow") and it.get("fill"):
            box = Image.new("RGBA", (int(w) + 2, int(h) + 2), (0, 0, 0, 0))
            ImageDraw.Draw(box).ellipse([1, 1, w + 1, h + 1], fill=(255, 255, 255, 255))
            self._shadow(box, (it["x"] - 1 / S, it["y"] - 1 / S))
        if it.get("fill"):
            a = 255 if it.get("alpha") is None else int(it["alpha"] * 255)
            self.draw.ellipse([x, y, x + w, y + h], fill=_rgb(it["fill"]) + (a,))
        if it.get("line"):
            self.draw.ellipse([x + lw / 2, y + lw / 2, x + w - lw / 2, y + h - lw / 2],
                              outline=_rgb(it["line"]), width=max(1, int(round(lw))))

    def _poly(self, it: Dict[str, Any]):
        S = self.S
        pts = [(p[0] * S, p[1] * S) for p in it["pts"]]
        lw = it.get("lw", 0.75) * S
        if it.get("fill"):
            a = 255 if it.get("alpha") is None else int(it["alpha"] * 255)
            self.draw.polygon(pts, fill=_rgb(it["fill"]) + (a,))
        if it.get("line") and it.get("close", True):
            self.draw.polygon(pts, outline=_rgb(it["line"]))
            self.draw.line(pts + [pts[0]], fill=_rgb(it["line"]),
                           width=max(1, int(round(lw))), joint="curve")
        elif it.get("line"):
            self.draw.line(pts, fill=_rgb(it["line"]), width=max(1, int(round(lw))),
                           joint="curve")

    def _path(self, it: Dict[str, Any]):
        S = self.S
        pts = [(p[0] * S, p[1] * S) for p in it["pts"]]
        lw = max(1, int(round(it.get("lw", 1.5) * S)))
        col = _rgb(it["line"]) if it.get("line") else (0, 0, 0)
        if it.get("alpha") is not None and it.get("line"):
            col = col + (int(it["alpha"] * 255),)
        if it.get("fill"):
            self.draw.polygon(pts, fill=_rgb(it["fill"]))
        if it.get("dash"):
            self._dashed(pts, col, lw, it["dash"])
        else:
            self.draw.line(pts, fill=col, width=lw, joint="curve")

    def _line(self, it: Dict[str, Any]):
        self._path(it)

    def _dashed(self, pts, col, lw, dash):
        d1, d2 = (dash if isinstance(dash, (tuple, list)) else (dash * 3, dash * 2))
        seg: List[Tuple[float, float]] = []
        for i in range(len(pts) - 1):
            seg.append(pts[i])
            seg.append(pts[i + 1])
        # 简化：按累计长度绘制虚线
        acc = 0.0
        drawing = True
        cur = [pts[0]]
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            L = math.hypot(x2 - x1, y2 - y1) or 1e-9
            steps = max(1, int(L / 2))
            for s in range(1, steps + 1):
                t = s / steps
                px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                acc += L / steps
                lim = (d1 if drawing else d2)
                cur.append((px, py))
                if acc >= lim:
                    if drawing:
                        self.draw.line(cur, fill=col, width=lw, joint="curve")
                    drawing = not drawing
                    cur = [(px, py)]
                    acc = 0.0
        if drawing and len(cur) > 1:
            self.draw.line(cur, fill=col, width=lw, joint="curve")

    def _image(self, it: Dict[str, Any]):
        S = self.S
        with Image.open(it["path"]) as im:
            im = im.convert("RGBA")
            tw, th = int(round(it["w"] * S)), int(round(it["h"] * S))
            im = im.resize((tw, th), Image.LANCZOS)
            if it.get("radius"):
                r = min(it["radius"] * S, min(tw, th) / 2.0)
                mask = Image.new("L", (tw, th), 0)
                ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw - 1, th - 1],
                                                       radius=r, fill=255)
                im.putalpha(Image.composite(im.split()[-1], Image.new("L", (tw, th), 0),
                                            mask))
        if it.get("shadow"):
            self._shadow(im, (it["x"], it["y"]))
        self.img.paste(im, (int(round(it["x"] * S)), int(round(it["y"] * S))), im)
        self.draw = ImageDraw.Draw(self.img, "RGBA")

    def _text(self, it: Dict[str, Any]):
        S = self.S
        for ln in it["lines"]:
            self._line_text(ln)

    def _line_text(self, ln: LayoutLine):
        S = self.S
        if ln.bullet:
            f = _dfont(ln.bullet_size, False, S)
            asc, desc = (v / S for v in f.getmetrics())
            by = ln.y + (ln.h - (asc + desc)) / 2.0 + asc
            self.draw.text((ln.bullet_x * S, by * S), ln.bullet, font=f,
                           fill=_rgb(ln.bullet_color), anchor="ls")
        x = ln.x
        sizes = [r.size for r in ln.runs] or [12.0]
        fm = _dfont(max(sizes), False, S).getmetrics()
        asc, desc = fm[0] / S, fm[1] / S
        base_y = ln.y + (ln.h - (asc + desc)) / 2.0 + asc
        for r in ln.runs:
            if not r.text:
                continue
            f = _dfont(r.size, r.bold, S)
            y = base_y - r.baseline * r.size
            self.draw.text((x * S, y * S), r.text, font=f, fill=_rgb(r.color),
                           anchor="ls",
                           stroke_width=max(1, int(round(0.55 * S))) if r.bold else 0,
                           stroke_fill=_rgb(r.color))
            x += text_width(r.text, r.size, r.bold)
