from __future__ import annotations

import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "metrics.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1200
HEIGHT = 680
BG = "#F7F5F0"
INK = "#182026"
MUTED = "#667078"
GRID = "#D8D4CC"
COLORS = ["#0F766E", "#D97706", "#2563EB", "#7C3AED", "#BE123C", "#4D7C0F"]
FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif"


def esc(value: object) -> str:
    return html.escape(str(value))


def text(x: float, y: float, value: object, size: int = 20, weight: int = 400,
         color: str = INK, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{esc(value)}</text>'
    )


def line(x1: float, y1: float, x2: float, y2: float, color: str = GRID, width: float = 1) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" />'


def rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0,
         stroke: str = "none", stroke_width: float = 0) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
    )


def svg_doc(body: list[str], title_value: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{esc(title_value)}">\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def trend_chart(key: str, item: dict) -> None:
    body = [rect(0, 0, WIDTH, HEIGHT, BG)]
    body.append(text(60, 65, f'{item["name"]}：2023-2025财务学习仪表板', 34, 700))
    body.append(text(60, 98, "先看趋势，再解释变化；不要只盯某一个增长率。", 18, 400, MUTED))

    chart_x, chart_y, chart_w, chart_h = 70, 155, 650, 350
    body.append(rect(chart_x, chart_y, chart_w, chart_h, "#FFFFFF", 18))
    body.append(text(chart_x + 24, chart_y + 40, "三年趋势（2023=100）", 22, 650))

    normalized = {
        name: [value / values[0] * 100 for value in values]
        for name, values in item["series"].items()
    }
    max_axis = max(140, math.ceil(max(max(values) for values in normalized.values()) / 20) * 20)
    min_axis = 60

    for i in range(5):
        y = chart_y + 80 + i * 55
        body.append(line(chart_x + 70, y, chart_x + chart_w - 30, y))
        axis_value = max_axis - i * (max_axis - min_axis) / 4
        body.append(text(chart_x + 55, y + 6, f"{axis_value:.0f}", 14, 400, MUTED, "end"))

    years = item["years"]
    xs = [chart_x + 125, chart_x + 335, chart_x + 545]
    for x, year in zip(xs, years):
        body.append(text(x, chart_y + chart_h - 24, year, 16, 500, MUTED, "middle"))

    legend_y = chart_y + chart_h + 52
    for idx, (name, values) in enumerate(item["series"].items()):
        indexes = normalized[name]
        points = []
        for x, value in zip(xs, indexes):
            y = chart_y + 80 + (max_axis - value) / (max_axis - min_axis) * 220
            points.append((x, y))
        color = COLORS[idx]
        body.append(
            f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" '
            f'fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />'
        )
        for point_idx, ((x, y), raw) in enumerate(zip(points, values)):
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}" />')
            # The three indexed series all begin at 100, so stagger the first
            # year. For later years, place revenue/cash labels below their
            # points and profit above to reduce collisions when lines converge.
            if point_idx == 0:
                label_y = y - 14 - idx * 18
            else:
                label_y = y + 20 if idx in (0, 2) else y - 16
            body.append(text(x, label_y, f"{raw:.1f}", 14, 600, color, "middle"))
        legend_x = chart_x + 30 + idx * 190
        body.append(rect(legend_x, legend_y - 14, 18, 5, color, 2))
        body.append(text(legend_x + 28, legend_y - 4, name, 16, 500))

    right_x, right_y, right_w, right_h = 760, 155, 370, 430
    body.append(rect(right_x, right_y, right_w, right_h, "#FFFFFF", 18))
    body.append(text(right_x + 24, right_y + 40, item["mix_title"], 22, 650))

    if "metric_pairs" in item:
        pair_y = right_y + 88
        for idx, (label, vals) in enumerate(item["metric_pairs"].items()):
            y = pair_y + idx * 78
            body.append(text(right_x + 24, y, label, 16, 500, MUTED))
            body.append(text(right_x + 190, y + 25, f"2024  {vals[0]:.2f}%", 15, 500, MUTED, "middle"))
            body.append(text(right_x + 310, y + 25, f"2025  {vals[1]:.2f}%", 15, 650, COLORS[0], "middle"))
            body.append(line(right_x + 24, y + 44, right_x + right_w - 24, y + 44))
    elif item.get("mix_is_percent"):
        max_value = max(item["mix"].values())
        start_y = right_y + 82
        for idx, (label, value) in enumerate(item["mix"].items()):
            y = start_y + idx * 53
            body.append(text(right_x + 24, y + 16, label, 15, 500))
            bar_x = right_x + 100
            bar_w = 205 * value / max_value
            body.append(rect(bar_x, y, bar_w, 22, COLORS[idx % len(COLORS)], 5))
            body.append(text(right_x + right_w - 24, y + 17, f"{value:.1f}%", 15, 650, INK, "end"))
    else:
        values = item["mix"]
        total = sum(values.values())
        bar_x, bar_y, bar_w, bar_h = right_x + 24, right_y + 88, right_w - 48, 40
        cursor = bar_x
        for idx, (label, value) in enumerate(values.items()):
            segment_w = bar_w * value / total
            body.append(rect(cursor, bar_y, segment_w, bar_h, COLORS[idx % len(COLORS)]))
            cursor += segment_w
        legend_y2 = bar_y + 76
        for idx, (label, value) in enumerate(values.items()):
            y = legend_y2 + idx * 42
            body.append(rect(right_x + 24, y - 14, 16, 16, COLORS[idx % len(COLORS)], 4))
            body.append(text(right_x + 52, y, label, 15, 500))
            body.append(text(right_x + right_w - 24, y, f"{value / total * 100:.1f}%", 15, 650, anchor="end"))

    note_y = 620
    for idx, note in enumerate(item.get("notes", [])):
        body.append(text(70, note_y + idx * 24, f"注：{note}" if idx == 0 else note, 15, 400, MUTED))

    (OUT / f"{key}_dashboard.svg").write_text(svg_doc(body, item["name"]), encoding="utf-8")


def cash_profile(item: dict) -> None:
    body = [rect(0, 0, WIDTH, HEIGHT, BG)]
    body.append(text(60, 65, "四类非金融企业的现金画像", 34, 700))
    body.append(text(60, 98, "现金转化率看利润含金量；资本开支强度看维持和扩张需要多少再投资。", 18, 400, MUTED))

    companies = item["companies"]
    conversion = item["cash_conversion"]
    capex = item["capex_to_cfo"]
    panels = [
        (70, 155, 500, 360, "现金转化率（倍）", conversion, 2.0, "x"),
        (630, 155, 500, 360, "资本开支强度（%）", capex, 70.0, "%"),
    ]
    for panel_x, panel_y, panel_w, panel_h, title_value, values, max_value, suffix in panels:
        body.append(rect(panel_x, panel_y, panel_w, panel_h, "#FFFFFF", 18))
        body.append(text(panel_x + 24, panel_y + 40, title_value, 22, 650))
        for idx, (company, value) in enumerate(zip(companies, values)):
            y = panel_y + 88 + idx * 66
            body.append(text(panel_x + 24, y + 19, company, 16, 500))
            bar_x = panel_x + 130
            bar_w = 275 * value / max_value
            body.append(rect(bar_x, y, bar_w, 28, COLORS[idx], 6))
            label = f"{value:.2f}x" if suffix == "x" else f"{value:.1f}%"
            body.append(text(panel_x + panel_w - 24, y + 21, label, 16, 650, INK, "end"))

    for idx, note in enumerate(item["notes"]):
        prefix = "注：" if idx == 0 else ""
        body.append(text(70, 565 + idx * 24, prefix + note, 15, 400, MUTED))

    (OUT / "cash_profile.svg").write_text(svg_doc(body, item["name"]), encoding="utf-8")


for chart_key in ["moutai", "midea", "shenhua", "cmb", "catl"]:
    trend_chart(chart_key, DATA[chart_key])

cash_profile(DATA["cash_profile"])
print(f"generated {len(list(OUT.glob('*.svg')))} charts in {OUT}")
