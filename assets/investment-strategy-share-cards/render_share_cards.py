from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1800
HEIGHT = 2400
MARGIN = 100

BG = "#F3F6F4"
SURFACE = "#FFFFFF"
INK = "#18232B"
MUTED = "#5D6A70"
NAVY = "#28506F"
GREEN = "#19734B"
TEAL = "#27848A"
AMBER = "#B97817"
RED = "#B13A3A"
PURPLE = "#65508C"
BORDER = "#D8E0DB"
SOFT_BLUE = "#E9F1F6"
SOFT_GREEN = "#E8F4ED"
SOFT_TEAL = "#E7F3F3"
SOFT_AMBER = "#FAF0DE"
SOFT_RED = "#F9EAEA"
SOFT_PURPLE = "#F0ECF6"


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


SERIES = font(31, True)
TITLE = font(82, True)
SUBTITLE = font(37)
H1 = font(53, True)
H2 = font(40, True)
BODY = font(34)
BODY_BOLD = font(34, True)
SMALL = font(28)
SMALL_BOLD = font(28, True)
TINY = font(24)
NUMBER = font(68, True)


def text_width(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap_text(draw, text, fnt, max_width):
    lines = []
    current = ""
    for char in text:
        candidate = current + char
        if not current or text_width(draw, candidate, fnt) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, text, x, y, max_width, fnt=BODY, fill=INK, line_height=52):
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def draw_bullets(draw, items, x, y, max_width, color, fnt=BODY, line_height=50, gap=20):
    for item in items:
        draw.ellipse((x, y + 17, x + 14, y + 31), fill=color)
        line_y = y
        for line in wrap_text(draw, item, fnt, max_width - 38):
            draw.text((x + 36, line_y), line, font=fnt, fill=INK)
            line_y += line_height
        y = line_y + gap
    return y


def rounded(draw, box, fill=SURFACE, outline=BORDER, radius=24, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, x, y, label, color, text_color="#FFFFFF"):
    pad_x = 24
    height = 52
    width = text_width(draw, label, SMALL_BOLD) + pad_x * 2
    draw.rounded_rectangle((x, y, x + width, y + height), radius=26, fill=color)
    draw.text((x + pad_x, y + 9), label, font=SMALL_BOLD, fill=text_color)
    return x + width


def card_header(draw, index, title, subtitle, accent):
    draw.text((MARGIN, 72), "投资流派小白科普", font=SERIES, fill=accent)
    draw.text((WIDTH - MARGIN, 72), f"{index:02d} / 06", font=SERIES, fill=MUTED, anchor="ra")
    title_y = 142
    title_end = draw_wrapped(draw, title, MARGIN, title_y, WIDTH - MARGIN * 2, TITLE, INK, 102)
    subtitle_end = draw_wrapped(
        draw,
        subtitle,
        MARGIN,
        title_end + 18,
        WIDTH - MARGIN * 2,
        SUBTITLE,
        MUTED,
        55,
    )
    draw.rounded_rectangle((MARGIN, subtitle_end + 30, WIDTH - MARGIN, subtitle_end + 42), radius=6, fill=accent)
    return subtitle_end + 82


def card_footer(draw, index):
    footer_y = HEIGHT - 118
    draw.line((MARGIN, footer_y - 24, WIDTH - MARGIN, footer_y - 24), fill=BORDER, width=2)
    draw.text(
        (MARGIN, footer_y),
        "教育资料｜案例与数字均为虚构演示｜不构成个性化投资建议",
        font=TINY,
        fill=MUTED,
    )
    draw.text((WIDTH - MARGIN, footer_y), f"INVESTING BASICS · {index:02d}", font=TINY, fill=MUTED, anchor="ra")


def ensure_content_fits(label, content_bottom):
    safe_bottom = HEIGHT - 165
    if content_bottom > safe_bottom:
        raise RuntimeError(f"{label} content overflow: {content_bottom} > {safe_bottom}")


def save(image, filename):
    target = OUT_DIR / filename
    image.save(target, format="PNG", optimize=True)
    print(f"generated {target.name} {image.size[0]}x{image.size[1]}")


def make_canvas(index, title, subtitle, accent):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    top = card_header(draw, index, title, subtitle, accent)
    card_footer(draw, index)
    return image, draw, top


def render_cover():
    image, draw, top = make_canvas(
        1,
        "投资策略，不是猜涨跌",
        "先弄清楚你赚的是什么钱、承担什么风险、什么时候必须退出。",
        NAVY,
    )

    rounded(draw, (MARGIN, top, WIDTH - MARGIN, top + 330), fill=INK, outline=INK, radius=32)
    draw.text((MARGIN + 48, top + 46), "一张图看懂 12 个投资流派", font=H1, fill="#FFFFFF")
    draw_wrapped(
        draw,
        "真正的策略包含四部分：收益来源、证据、仓位和退出。只知道“买什么”，还不算拥有策略。",
        MARGIN + 48,
        top + 126,
        WIDTH - MARGIN * 2 - 96,
        BODY,
        "#DCE6EA",
        54,
    )

    layers = [
        ("01", "组合框架", "被动指数 · 资产配置", "决定钱放在哪里", NAVY, SOFT_BLUE),
        ("02", "基本面选股", "价值 · 成长 · 质量 · 股息", "决定长期持有什么", GREEN, SOFT_GREEN),
        ("03", "系统与周期", "趋势 · 宏观 · 量化", "决定按什么规则调整", TEAL, SOFT_TEAL),
        ("04", "专业机会交易", "事件 · 相对价值 · 专业投机", "决定特殊机会的赔率", AMBER, SOFT_AMBER),
    ]
    y = top + 370
    gap = 24
    row_h = 244
    for number, name, schools, answer, color, fill in layers:
        rounded(draw, (MARGIN, y, WIDTH - MARGIN, y + row_h), fill=fill, outline=color, radius=26, width=3)
        draw.text((MARGIN + 38, y + 48), number, font=NUMBER, fill=color)
        draw.text((MARGIN + 172, y + 40), name, font=H1, fill=INK)
        draw.text((MARGIN + 172, y + 112), schools, font=BODY_BOLD, fill=color)
        draw.text((WIDTH - MARGIN - 36, y + 160), answer, font=SMALL, fill=MUTED, anchor="ra")
        y += row_h + gap

    note_y = y + 14
    rounded(draw, (MARGIN, note_y, WIDTH - MARGIN, note_y + 230), fill=SURFACE, outline=BORDER)
    draw.text((MARGIN + 36, note_y + 32), "小白起点", font=H2, fill=RED)
    draw_bullets(
        draw,
        [
            "先从宽基指数或基础资产配置理解长期收益与回撤。",
            "再学一种增强方法；事件、套利和专业投机放到最后。",
        ],
        MARGIN + 40,
        note_y + 94,
        WIDTH - MARGIN * 2 - 80,
        RED,
        SMALL,
        43,
        10,
    )
    ensure_content_fits("cover", note_y + 230)
    save(image, "01-investing-schools-cover.png")


def render_school_map():
    image, draw, top = make_canvas(
        2,
        "12 个流派，其实分四层",
        "它们不是同一道选择题：有的决定组合，有的决定选股，有的决定交易时机。",
        GREEN,
    )
    layers = [
        ("第一层", "组合框架", "钱放在哪里？", ["被动指数", "资产配置"], "先定期限、现金和股债比例", NAVY, SOFT_BLUE),
        (
            "第二层",
            "基本面选股",
            "长期持有什么？",
            ["价值", "成长", "质量/护城河", "股息/现金流"],
            "再看估值、增长、现金流和竞争优势",
            GREEN,
            SOFT_GREEN,
        ),
        (
            "第三层",
            "系统与周期",
            "什么时候调整？",
            ["趋势/动量", "宏观/周期", "量化/因子"],
            "必须有统一信号、复核周期和成本约束",
            TEAL,
            SOFT_TEAL,
        ),
        (
            "第四层",
            "专业机会交易",
            "特殊机会赔率如何？",
            ["事件驱动", "套利/相对价值", "专业投机"],
            "先算失败损失、流动性和杠杆风险",
            AMBER,
            SOFT_AMBER,
        ),
    ]
    y = top
    row_h = 380
    for tag, name, question, schools, note, color, fill in layers:
        rounded(draw, (MARGIN, y, WIDTH - MARGIN, y + row_h), fill=fill, outline=color, radius=28, width=3)
        pill(draw, MARGIN + 36, y + 34, tag, color)
        draw.text((MARGIN + 36, y + 112), name, font=H1, fill=INK)
        draw.text((WIDTH - MARGIN - 36, y + 123), question, font=BODY_BOLD, fill=color, anchor="ra")
        school_x = MARGIN + 36
        school_y = y + 205
        for school in schools:
            next_x = pill(draw, school_x, school_y, school, color)
            if next_x > WIDTH - MARGIN - 260:
                school_x = MARGIN + 36
                school_y += 72
                next_x = pill(draw, school_x, school_y, school, color)
            school_x = next_x + 14
        draw.text((MARGIN + 36, y + 325), note, font=SMALL, fill=MUTED)
        y += row_h + 18

    rounded(draw, (MARGIN, y + 8, WIDTH - MARGIN, y + 198), fill=SOFT_RED, outline=RED, radius=24, width=3)
    draw.text((MARGIN + 38, y + 42), "最重要的边界", font=H2, fill=RED)
    draw_wrapped(
        draw,
        "可以跨层组合，但同一笔交易不能在亏损后临时换规则：价值投资看逻辑止损，趋势交易看价格止损。",
        MARGIN + 38,
        y + 104,
        WIDTH - MARGIN * 2 - 76,
        SMALL,
        INK,
        43,
    )
    ensure_content_fits("school map", y + 198)
    save(image, "02-investing-schools-map.png")


def render_selection_route():
    image, draw, top = make_canvas(
        3,
        "新手怎么选第一个流派？",
        "先按时间、能力和纪律选择起点，不按最近谁涨得最好选择。",
        TEAL,
    )

    rounded(draw, (MARGIN, top, WIDTH - MARGIN, top + 190), fill=INK, outline=INK, radius=28)
    draw.text((WIDTH // 2, top + 44), "第一问：你每周能投入多少研究时间？", font=H2, fill="#FFFFFF", anchor="ma")
    draw.text(
        (WIDTH // 2, top + 116),
        "时间越少，越应该依赖分散、低成本和低频规则。",
        font=SMALL,
        fill="#DCE6EA",
        anchor="ma",
    )

    routes = [
        (
            "几乎没有",
            "从这里开始",
            "被动指数 + 基础资产配置",
            ["学会定投与再平衡", "先理解最大回撤", "不追逐短期热点"],
            NAVY,
            SOFT_BLUE,
        ),
        (
            "愿意读财报",
            "学习后使用",
            "价值 / 质量 / 成长 / 股息",
            ["只选一种主方法", "按财报周期复核", "写清逻辑退出条件"],
            GREEN,
            SOFT_GREEN,
        ),
        (
            "能严格执行规则",
            "先模拟记录",
            "趋势 / 简单因子",
            ["先定义价格止损", "接受连续小亏", "统计真实费用与滑点"],
            TEAL,
            SOFT_TEAL,
        ),
        (
            "能深度跟踪",
            "进阶后再做",
            "宏观 / 量化 / 事件 / 套利 / 投机",
            ["理解模型和条款", "能评估尾部风险", "不依赖杠杆翻本"],
            AMBER,
            SOFT_AMBER,
        ),
    ]
    y = top + 226
    box_w = (WIDTH - MARGIN * 2 - 28) // 2
    box_h = 670
    for idx, (time, level, route, bullets, color, fill) in enumerate(routes):
        x = MARGIN + (idx % 2) * (box_w + 28)
        y_box = y + (idx // 2) * (box_h + 28)
        rounded(draw, (x, y_box, x + box_w, y_box + box_h), fill=fill, outline=color, radius=28, width=3)
        pill(draw, x + 34, y_box + 34, time, color)
        draw.text((x + 34, y_box + 116), level, font=SMALL_BOLD, fill=color)
        route_end = draw_wrapped(draw, route, x + 34, y_box + 164, box_w - 68, H2, INK, 56)
        draw.line((x + 34, route_end + 24, x + box_w - 34, route_end + 24), fill=color, width=3)
        draw_bullets(draw, bullets, x + 36, route_end + 60, box_w - 72, color, SMALL, 44, 18)

    bottom = y + box_h * 2 + 28 + 32
    rounded(draw, (MARGIN, bottom, WIDTH - MARGIN, bottom + 208), fill=SOFT_RED, outline=RED, radius=28, width=3)
    draw.text((MARGIN + 38, bottom + 34), "无论选哪条路线，都先回答", font=H2, fill=RED)
    draw_wrapped(
        draw,
        "这笔钱何时要用？最多能承受多大回撤？哪些证据会证明自己错了？",
        MARGIN + 38,
        bottom + 104,
        WIDTH - MARGIN * 2 - 76,
        BODY_BOLD,
        INK,
        53,
    )
    ensure_content_fits("selection route", bottom + 208)
    save(image, "03-beginner-selection-route.png")


def render_risk_budget():
    image, draw, top = make_canvas(
        4,
        "先算能亏多少，再算买多少",
        "仓位控制不是保守，而是让一次判断错误不会结束整个投资计划。",
        RED,
    )

    left_x = MARGIN
    gap = 28
    col_w = (WIDTH - MARGIN * 2 - gap) // 2
    right_x = left_x + col_w + gap
    panel_h = 875

    rounded(draw, (left_x, top, left_x + col_w, top + panel_h), fill=SURFACE, outline=BORDER, radius=28)
    draw.text((left_x + 34, top + 34), "回撤越深，回本越难", font=H2, fill=RED)
    rows = [("-10%", "+11.1%"), ("-20%", "+25.0%"), ("-30%", "+42.9%"), ("-40%", "+66.7%"), ("-50%", "+100.0%")]
    y = top + 130
    for drawdown, recovery in rows:
        draw.text((left_x + 42, y), drawdown, font=BODY_BOLD, fill=RED)
        draw.rounded_rectangle((left_x + 190, y + 8, left_x + 190 + int(drawdown[1:-1]) * 7, y + 42), radius=17, fill=RED)
        draw.text((left_x + col_w - 36, y), recovery, font=BODY_BOLD, fill=GREEN, anchor="ra")
        y += 122
    draw.text((left_x + 42, top + 770), "左：账户回撤　右：回本所需涨幅", font=SMALL, fill=MUTED)

    rounded(draw, (right_x, top, right_x + col_w, top + panel_h), fill=SOFT_BLUE, outline=NAVY, radius=28, width=3)
    draw.text((right_x + 34, top + 34), "演示：交易型仓位", font=H2, fill=NAVY)
    draw.text((right_x + 36, top + 130), "账户资金", font=SMALL, fill=MUTED)
    draw.text((right_x + col_w - 36, top + 124), "100,000 元", font=BODY_BOLD, fill=INK, anchor="ra")
    draw.text((right_x + 36, top + 206), "单笔最多亏损", font=SMALL, fill=MUTED)
    draw.text((right_x + col_w - 36, top + 200), "500 元", font=BODY_BOLD, fill=INK, anchor="ra")
    draw.text((right_x + 36, top + 282), "止损距离", font=SMALL, fill=MUTED)
    draw.text((right_x + col_w - 36, top + 276), "5%", font=BODY_BOLD, fill=INK, anchor="ra")
    draw.line((right_x + 36, top + 354, right_x + col_w - 36, top + 354), fill=NAVY, width=3)
    draw.text((right_x + 36, top + 400), "仓位 = 允许亏损 ÷ 止损比例", font=SMALL_BOLD, fill=NAVY)
    draw.text((right_x + 36, top + 486), "500 ÷ 5%", font=H1, fill=INK)
    draw.text((right_x + col_w - 36, top + 486), "= 10,000 元", font=H1, fill=GREEN, anchor="ra")
    draw_wrapped(
        draw,
        "演示值，不是建议值。跳空、滑点、费用和流动性可能使实际亏损更高。",
        right_x + 36,
        top + 620,
        col_w - 72,
        SMALL,
        RED,
        45,
    )

    y2 = top + panel_h + 30
    draw.text((MARGIN, y2), "三种退出机制，不要混用", font=H1, fill=INK)
    exits = [
        ("逻辑止损", "价值 / 成长 / 质量 / 股息", "基本面假设被证伪", GREEN, SOFT_GREEN),
        ("价格止损", "趋势 / 技术交易", "价格达到预设边界", RED, SOFT_RED),
        ("配置再平衡", "指数 / 资产配置", "权重偏离目标区间", NAVY, SOFT_BLUE),
    ]
    y2 += 88
    row_h = 245
    for title, fit, trigger, color, fill in exits:
        rounded(draw, (MARGIN, y2, WIDTH - MARGIN, y2 + row_h), fill=fill, outline=color, radius=26, width=3)
        draw.text((MARGIN + 36, y2 + 34), title, font=H2, fill=color)
        draw.text((MARGIN + 36, y2 + 105), fit, font=SMALL_BOLD, fill=INK)
        draw.text((WIDTH - MARGIN - 36, y2 + 105), trigger, font=SMALL, fill=MUTED, anchor="ra")
        y2 += row_h + 24
    ensure_content_fits("risk budget", y2 - 24)
    save(image, "04-risk-budget-basics.png")


def render_same_asset_rules():
    image, draw, top = make_canvas(
        5,
        "同样下跌 15%，答案可能完全不同",
        "涨跌只是结果。不同流派先检查的证据、允许的动作和退出条件并不一样。",
        PURPLE,
    )

    rounded(draw, (MARGIN, top, WIDTH - MARGIN, top + 226), fill=INK, outline=INK, radius=28)
    draw.text((WIDTH // 2, top + 42), "虚构场景：资产甲从 100 元跌到 85 元", font=H1, fill="#FFFFFF", anchor="ma")
    draw.text(
        (WIDTH // 2, top + 132),
        "不要先问“该不该补仓”，先问“我原来按什么方法买入”。",
        font=SMALL,
        fill="#DCE6EA",
        anchor="ma",
    )

    cases = [
        (
            "被动指数",
            "先检查",
            "期限、目标权重、基金质量",
            "可能动作",
            "按原定投或再平衡规则处理",
            "不应该",
            "因恐慌突然清仓，或临时加倍押注",
            NAVY,
            SOFT_BLUE,
        ),
        (
            "价值投资",
            "先检查",
            "内在价值、现金流、债务是否变化",
            "可能动作",
            "逻辑未变且安全边际扩大时有限加仓",
            "不应该",
            "只因为更便宜就无限摊平",
            GREEN,
            SOFT_GREEN,
        ),
        (
            "成长投资",
            "先检查",
            "增长、留存、毛利率和估值预期",
            "可能动作",
            "数据兑现且估值合理时持有或加仓",
            "不应该",
            "用远期故事掩盖当期经营恶化",
            TEAL,
            SOFT_TEAL,
        ),
        (
            "趋势交易",
            "先检查",
            "是否触发入场前写好的价格止损",
            "可能动作",
            "触发即退出，未触发则按系统持有",
            "不应该",
            "取消止损并改口说要长期投资",
            RED,
            SOFT_RED,
        ),
    ]
    y = top + 260
    box_w = (WIDTH - MARGIN * 2 - 28) // 2
    box_h = 650
    for idx, (name, label1, check, label2, action, label3, wrong, color, fill) in enumerate(cases):
        x = MARGIN + (idx % 2) * (box_w + 28)
        y_box = y + (idx // 2) * (box_h + 28)
        rounded(draw, (x, y_box, x + box_w, y_box + box_h), fill=fill, outline=color, radius=28, width=3)
        draw.text((x + 34, y_box + 34), name, font=H1, fill=color)
        ty = y_box + 130
        for label, content, content_color in [
            (label1, check, INK),
            (label2, action, INK),
            (label3, wrong, RED),
        ]:
            draw.text((x + 36, ty), label, font=SMALL_BOLD, fill=color if label != "不应该" else RED)
            ty = draw_wrapped(draw, content, x + 36, ty + 48, box_w - 72, SMALL, content_color, 45) + 30

    bottom = y + box_h * 2 + 28 + 30
    rounded(draw, (MARGIN, bottom, WIDTH - MARGIN, bottom + 195), fill=SOFT_PURPLE, outline=PURPLE, radius=28, width=3)
    draw.text((WIDTH // 2, bottom + 36), "规则一致性 > 临场聪明", font=H1, fill=PURPLE, anchor="ma")
    draw.text(
        (WIDTH // 2, bottom + 120),
        "同一笔交易只能有一套主要收益逻辑和退出机制。",
        font=SMALL_BOLD,
        fill=INK,
        anchor="ma",
    )
    ensure_content_fits("same asset rules", bottom + 195)
    save(image, "05-same-asset-different-rules.png")


def render_plan_checklist():
    image, draw, top = make_canvas(
        6,
        "下单前，先写完这五问",
        "能写清楚，才说明你拥有计划；写不清楚，就只是对价格有一个愿望。",
        AMBER,
    )

    questions = [
        ("01", "我采用什么流派？", "指数、价值、成长、趋势……只能先确定一套主要规则。", NAVY, SOFT_BLUE),
        ("02", "收益预计从哪里来？", "市场增长、低估修复、企业成长、现金流、趋势、事件还是价差？", GREEN, SOFT_GREEN),
        ("03", "哪些证据支持买入？", "写可验证的事实，不写“感觉会涨”“大家都在买”。", TEAL, SOFT_TEAL),
        ("04", "最坏情况是什么？", "价格、逻辑、流动性、杠杆和资金期限分别可能怎样伤害我？", RED, SOFT_RED),
        ("05", "何时加仓、减仓和退出？", "所有条件必须在下单前定义，不能等情绪最强时决定。", AMBER, SOFT_AMBER),
    ]
    y = top
    row_h = 252
    for number, title, note, color, fill in questions:
        rounded(draw, (MARGIN, y, WIDTH - MARGIN, y + row_h), fill=fill, outline=color, radius=26, width=3)
        draw.text((MARGIN + 34, y + 46), number, font=NUMBER, fill=color)
        draw.text((MARGIN + 176, y + 38), title, font=H2, fill=INK)
        draw_wrapped(draw, note, MARGIN + 176, y + 108, WIDTH - MARGIN * 2 - 218, SMALL, MUTED, 44)
        y += row_h + 24

    draw.text((MARGIN, y + 14), "一页计划至少写下", font=H1, fill=INK)
    tags = [
        ("买入证据", NAVY),
        ("初始仓位", GREEN),
        ("仓位上限", TEAL),
        ("加仓条件", PURPLE),
        ("退出条件", RED),
        ("复核日期", AMBER),
    ]
    y += 112
    tag_x = MARGIN
    tag_y = y
    for label, color in tags:
        next_x = pill(draw, tag_x, tag_y, label, color)
        if next_x > WIDTH - MARGIN - 240:
            tag_x = MARGIN
            tag_y += 82
            next_x = pill(draw, tag_x, tag_y, label, color)
        tag_x = next_x + 18

    note_y = tag_y + 110
    rounded(draw, (MARGIN, note_y, WIDTH - MARGIN, note_y + 220), fill=INK, outline=INK, radius=28)
    draw.text((MARGIN + 38, note_y + 34), "最后提醒", font=H2, fill="#FFFFFF")
    draw_wrapped(
        draw,
        "一次盈利不能证明方法正确，一次亏损也不能自动证明方法错误。复盘要看过程是否遵守规则、结果能否重复。",
        MARGIN + 38,
        note_y + 100,
        WIDTH - MARGIN * 2 - 76,
        SMALL,
        "#DCE6EA",
        44,
    )
    ensure_content_fits("plan checklist", note_y + 220)
    save(image, "06-investment-plan-checklist.png")


def main():
    render_cover()
    render_school_map()
    render_selection_route()
    render_risk_budget()
    render_same_asset_rules()
    render_plan_checklist()


if __name__ == "__main__":
    main()
