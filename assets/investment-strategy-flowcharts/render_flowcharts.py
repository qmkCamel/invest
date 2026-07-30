from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path(__file__).resolve().parent

WIDTH = 1920
HEIGHT = 1080
MARGIN_X = 70
CARD_GAP = 24
TOP = 190
CARD_H = 730
CARD_W = (WIDTH - MARGIN_X * 2 - CARD_GAP * 4) // 5

BG = "#f6f7f5"
INK = "#202529"
MUTED = "#5a6369"
BORDER = "#d7ddd7"
WHITE = "#ffffff"

HEADER_COLORS = {
    "关注指标": "#304b66",
    "建仓": "#247455",
    "加仓": "#2f7f89",
    "止盈/减仓": "#a66b1f",
    "止损/退出": "#9c3838",
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


TITLE_FONT = font(54, True)
SUBTITLE_FONT = font(28)
HEADER_FONT = font(29, True)
BODY_FONT = font(24)
FOOT_FONT = font(21)


def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, fnt, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            candidate = current + char
            if text_width(draw, candidate, fnt) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
    return lines


def draw_arrow(draw, start, end, color="#667076"):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=4)
    draw.polygon([(x2, y2), (x2 - 14, y2 - 9), (x2 - 14, y2 + 9)], fill=color)


def draw_card(draw, x, y, title, lines):
    draw.rounded_rectangle((x, y, x + CARD_W, y + CARD_H), radius=26, fill=WHITE, outline=BORDER, width=2)
    draw.rounded_rectangle((x, y, x + CARD_W, y + 74), radius=26, fill=HEADER_COLORS[title])
    draw.rectangle((x, y + 42, x + CARD_W, y + 74), fill=HEADER_COLORS[title])
    draw.text((x + 24, y + 19), title, fill="#ffffff", font=HEADER_FONT)

    cursor_y = y + 104
    max_width = CARD_W - 48
    for item in lines:
        wrapped = wrap_text(draw, item, BODY_FONT, max_width - 22)
        draw.ellipse((x + 24, cursor_y + 10, x + 34, cursor_y + 20), fill=HEADER_COLORS[title])
        for idx, line in enumerate(wrapped):
            draw.text((x + 46, cursor_y), line, fill=INK, font=BODY_FONT)
            cursor_y += 34
        cursor_y += 18


def draw_flowchart(spec):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.text((MARGIN_X, 54), spec["title"], fill=INK, font=TITLE_FONT)
    draw.text((MARGIN_X, 124), spec["subtitle"], fill=MUTED, font=SUBTITLE_FONT)

    x_positions = [MARGIN_X + i * (CARD_W + CARD_GAP) for i in range(5)]
    headings = ["关注指标", "建仓", "加仓", "止盈/减仓", "止损/退出"]
    for idx, heading in enumerate(headings):
        draw_card(draw, x_positions[idx], TOP, heading, spec["cards"][heading])

    arrow_y = TOP + CARD_H + 45
    for idx in range(4):
        start_x = x_positions[idx] + CARD_W + 6
        end_x = x_positions[idx + 1] - 6
        draw_arrow(draw, (start_x, arrow_y), (end_x, arrow_y))

    draw.text(
        (MARGIN_X, HEIGHT - 60),
        "执行口径：先定义仓位和退出条件，再处理买卖动作；长期投资看逻辑失效，交易策略看价格触发。",
        fill=MUTED,
        font=FOOT_FONT,
    )

    image.save(OUT_DIR / spec["file"], quality=95)


SPECS = [
    {
        "file": "passive-index.png",
        "title": "被动指数派：定投与再平衡",
        "subtitle": "赚市场长期 Beta，重点是低成本、分散和纪律持有。",
        "cards": {
            "关注指标": ["指数覆盖范围", "费用率与跟踪误差", "基金规模与流动性", "估值分位与最大回撤"],
            "建仓": ["选择低费率宽基产品", "用定投或分批降低择时压力", "先确定目标权益仓位"],
            "加仓": ["按固定周期投入新增资金", "回撤或估值下降时补充", "目标权重低于计划时再平衡"],
            "止盈/减仓": ["不因短期盈利卖出", "权益仓位超过上限时减仓", "估值极端偏高时再平衡"],
            "止损/退出": ["通常不做短线止损", "基金跟踪失真或流动性恶化", "投资期限或风险承受变化"],
        },
    },
    {
        "file": "asset-allocation.png",
        "title": "资产配置派：目标权重与风险预算",
        "subtitle": "用股票、债券、现金、黄金等资产组合管理收益和回撤。",
        "cards": {
            "关注指标": ["目标权重与偏离幅度", "利率、通胀与债券收益率", "资产相关性和波动率", "组合回撤与现金需求"],
            "建仓": ["先定大类资产比例", "按风险预算分批买入", "保留现金缓冲"],
            "加仓": ["低配资产回补目标权重", "估值或收益率改善时加仓", "避免单一资产过度集中"],
            "止盈/减仓": ["涨多资产超配时卖出", "组合风险超过预算时降仓", "用再平衡回到目标区间"],
            "止损/退出": ["资金期限变化时重设配置", "风险承受下降时降权益", "不因单一资产短跌全盘退出"],
        },
    },
    {
        "file": "value-investing.png",
        "title": "价值投资派：安全边际与低估修复",
        "subtitle": "价格低于保守价值时买入，等待估值修复或基本面改善。",
        "cards": {
            "关注指标": ["PE、PB、EV/EBITDA", "自由现金流收益率", "资产负债率与净现金", "ROE、分红和行业周期"],
            "建仓": ["估算保守内在价值", "折价足够才分批买入", "留出安全边际"],
            "加仓": ["价格更低但基本面未坏", "经营拐点被验证", "折价扩大且风险可控"],
            "止盈/减仓": ["价格接近合理价值", "折价修复完成", "出现更高赔率机会时换仓"],
            "止损/退出": ["估值假设被证伪", "现金流和债务明显恶化", "管理层失信或行业永久衰退"],
        },
    },
    {
        "file": "growth-investing.png",
        "title": "成长投资派：增长兑现与估值匹配",
        "subtitle": "为未来增长支付溢价，但必须持续验证增长质量。",
        "cards": {
            "关注指标": ["收入和利润增速", "毛利率、留存率和用户增长", "单位经济模型", "市场空间与估值/增长匹配"],
            "建仓": ["增长确定性较高", "商业模式可验证", "估值未明显透支时分批"],
            "加仓": ["增长数据继续兑现", "利润率改善", "新业务或竞争优势被验证"],
            "止盈/减仓": ["增速下台阶", "估值显著透支", "渗透率接近天花板或仓位过重"],
            "止损/退出": ["增长逻辑失败", "客户流失或毛利率结构性下滑", "现金消耗失控"],
        },
    },
    {
        "file": "quality-moat.png",
        "title": "质量/护城河派：优秀公司长期复利",
        "subtitle": "关注资本回报、现金流质量和竞争优势，而不是单纯便宜。",
        "cards": {
            "关注指标": ["ROE、ROIC 和自由现金流", "毛利率稳定性", "市场份额和客户粘性", "管理层资本配置"],
            "建仓": ["确认长期好生意", "价格进入合理区间", "不强求最低估值"],
            "加仓": ["护城河增强", "业绩质量稳定", "短期波动带来合理价格"],
            "止盈/减仓": ["估值极端高", "预期收益率明显下降", "单一持仓超出组合上限"],
            "止损/退出": ["护城河被削弱", "资本回报率长期下滑", "现金流质量或治理恶化"],
        },
    },
    {
        "file": "dividend-cashflow.png",
        "title": "股息/现金流派：现金回报可持续",
        "subtitle": "追求可见现金流，但高股息必须由真实现金流支撑。",
        "cards": {
            "关注指标": ["股息率和分红率", "自由现金流覆盖倍数", "负债期限和利息覆盖", "派息历史与监管政策"],
            "建仓": ["股息率有吸引力", "分红覆盖充分", "主业现金流稳定"],
            "加仓": ["股价回落但现金流未坏", "分红安全边际提高", "组合现金回报需要补充"],
            "止盈/减仓": ["价格上涨压低股息率", "利率环境变化", "仓位超配时再平衡"],
            "止损/退出": ["分红被削减", "现金流无法覆盖分红", "负债再融资压力上升"],
        },
    },
    {
        "file": "trend-momentum.png",
        "title": "趋势/动量派：强者恒强与纪律止损",
        "subtitle": "顺着价格趋势试错，用明确止损控制震荡市损耗。",
        "cards": {
            "关注指标": ["均线斜率和突破结构", "价格新高/新低", "相对强弱和成交量", "波动率、行业强弱和回撤"],
            "建仓": ["突破关键区间", "站上趋势均线", "相对强度排名靠前时试仓"],
            "加仓": ["突破后回踩不破", "趋势继续延续", "波动率可控时金字塔加仓"],
            "止盈/减仓": ["趋势加速过热", "相对强度下降", "跌破短期趋势线或达到目标"],
            "止损/退出": ["跌破关键均线或前低", "跌破突破位或 ATR 止损线", "单笔亏损触达上限"],
        },
    },
    {
        "file": "macro-cycle.png",
        "title": "宏观/周期派：阶段判断与资产切换",
        "subtitle": "用增长、通胀、利率和信用周期判断哪些资产更占优。",
        "cards": {
            "关注指标": ["PMI、CPI、PPI", "利率和收益率曲线", "信用利差与汇率", "库存、政策和盈利周期"],
            "建仓": ["宏观阶段与资产逻辑匹配", "价格尚未充分反映", "分批进入受益资产"],
            "加仓": ["数据连续验证同一方向", "政策继续支持", "资产价格仍有赔率"],
            "止盈/减仓": ["周期进入下一阶段", "政策边际转向", "交易拥挤或估值充分反映"],
            "止损/退出": ["核心宏观假设反向", "走势长期背离判断", "损失超过风险预算"],
        },
    },
    {
        "file": "quant-factor.png",
        "title": "量化/因子派：规则、暴露与再平衡",
        "subtitle": "用系统规则捕捉因子溢价，重点防过拟合和实盘漂移。",
        "cards": {
            "关注指标": ["因子暴露和经济解释", "信息比率和最大回撤", "换手率、交易成本和容量", "行业和风格偏离"],
            "建仓": ["因子可解释且不过拟合", "成本和容量可承受", "组合分散后按规则买入"],
            "加仓": ["按模型再平衡", "目标因子暴露不足时调整", "不凭主观情绪加仓"],
            "止盈/减仓": ["因子信号衰减", "仓位或行业偏离过大", "组合风险超过预算"],
            "止损/退出": ["实盘回撤超过压力测试", "交易成本显著上升", "数据质量问题或因子拥挤"],
        },
    },
    {
        "file": "event-driven.png",
        "title": "事件驱动派：事件概率与价差收敛",
        "subtitle": "围绕明确事件定价，收益必须覆盖失败损失和资金时间成本。",
        "cards": {
            "关注指标": ["事件条款和审批概率", "时间表与监管态度", "价差和失败损失", "对手方信用和资金成本"],
            "建仓": ["事件真实且条款清晰", "预期收益覆盖失败损失", "时间成本可接受"],
            "加仓": ["审批或投票进展提高成功率", "价差仍有吸引力", "失败损失没有扩大"],
            "止盈/减仓": ["价差大幅收敛", "事件临近落地", "收益率不再覆盖风险"],
            "止损/退出": ["事件失败或条款变差", "审批延迟超预期", "信用恶化或价格暗示失败"],
        },
    },
    {
        "file": "relative-value-arbitrage.png",
        "title": "套利/相对价值派：价差偏离与收敛机制",
        "subtitle": "关注两个相关价格的偏离，不把套利误认为无风险。",
        "cards": {
            "关注指标": ["折溢价、基差和利差", "相关性与回归速度", "融资成本和保证金", "流动性与交易规则"],
            "建仓": ["偏离超过历史区间和成本", "存在明确收敛机制", "对冲和流动性可执行"],
            "加仓": ["价差扩大但机制未变", "保证金充足", "有限加仓而非无限摊平"],
            "止盈/减仓": ["价差回归目标区间", "资金效率下降", "风险收益不再划算"],
            "止损/退出": ["收敛机制失效", "相关性断裂", "保证金、规则或流动性恶化"],
        },
    },
    {
        "file": "professional-speculation.png",
        "title": "专业投机/技术交易派：赔率、止损与趋势证伪",
        "subtitle": "先定义风险，再等待信号；错了小亏，对了让利润奔跑。",
        "cards": {
            "关注指标": ["趋势结构和支撑阻力", "1-2-3 反转与 2B 假突破", "成交量、ATR 和波动率", "胜率、盈亏比和仓位风险"],
            "建仓": ["出现明确交易信号", "止损位和目标位清楚", "盈亏比足够时小仓试错"],
            "加仓": ["只有浮盈保护后加仓", "沿趋势回踩或突破递进", "同步上移止损"],
            "止盈/减仓": ["达到目标位", "趋势衰竭或出现反向信号", "赔率下降时分批兑现"],
            "止损/退出": ["入场理由失效", "跌破止损位", "单笔亏损达到上限即退出"],
        },
    },
]


def main():
    for spec in SPECS:
        draw_flowchart(spec)
    print(f"generated {len(SPECS)} PNG files in {OUT_DIR}")


if __name__ == "__main__":
    main()
