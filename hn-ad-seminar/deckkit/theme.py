# -*- coding: utf-8 -*-
"""学术科研风视觉体系：深蓝 + 青绿。所有颜色为 6 位 HEX（不带 #）。"""

# ---------- 主色 ----------
NAVY = "0F3D6E"      # 主色：学术深蓝
NAVY_D = "0A2A4D"    # 深蓝加深（封面/标题底）
NAVY_L = "1C5590"    # 深蓝提亮
TEAL = "12A08C"      # 强调：青绿（氮循环 / 生态）
TEAL_D = "0B7A6B"
TEAL_L = "E2F4F1"

# ---------- 中性色 ----------
INK = "1B2A38"       # 正文
GRAY = "5C6B7A"      # 次要文字
GRAY_L = "94A2B1"    # 弱文字 / 页脚
LINE = "DCE4EC"      # 分隔线 / 描边
BG_SOFT = "F5F8FB"   # 浅底卡片
BG_SOFT2 = "EBF1F7"
WHITE = "FFFFFF"

# ---------- 语义色 ----------
AMBER = "DD8A2B"     # 氨氮 / 痛点 / 臭气
AMBER_L = "FCF2E2"
RED = "C6434B"       # 亚硝酸盐 / 一票否决
RED_L = "FAEBED"
GREEN = "2E9A5B"     # 硝酸盐 / 保氮
GREEN_L = "E8F5ED"
BLUE = "2A6FB0"      # 总氮 / 信息
BLUE_L = "E8F0F9"

# 氮素形态配色（全篇统一）
N_COLOR = {
    "NH4": AMBER,
    "NO2": RED,
    "NO3": GREEN,
    "N2": NAVY_L,
    "TN": BLUE,
}

# ---------- 字体 ----------
F_EA = "Microsoft YaHei"   # 中文（微软雅黑，Windows/WPS 通用）
F_LATIN = "Arial"          # 西文与数字
F_PREVIEW = "cjk_preview.ttf"   # 仅用于本仓库内 PNG 预览（Droid Sans Fallback）

# ---------- 画布 ----------
SLIDE_W = 960.0   # pt  (13.333 in)
SLIDE_H = 540.0   # pt  (7.5 in)
M = 48.0          # 页边距
CW = SLIDE_W - 2 * M   # 内容宽 864

# 内容页版式基线
HEAD_Y = 34.0      # 标题顶
HEAD_H = 34.0
BODY_Y = 104.0     # 正文区顶
BODY_B = 486.0     # 正文区底
FOOT_Y = 500.0
