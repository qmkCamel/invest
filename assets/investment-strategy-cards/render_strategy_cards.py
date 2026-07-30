from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 2400
HEIGHT = 1600
MARGIN = 86
GAP = 32

BG = "#f4f6f2"
SURFACE = "#ffffff"
INK = "#1f2529"
MUTED = "#5d666b"
BORDER = "#d7ded8"
LINE = "#e4e9e3"

BLUE = "#2f4f6f"
GREEN = "#23734f"
TEAL = "#2e838b"
AMBER = "#aa711d"
RED = "#a83a3a"


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


TITLE = font(64, True)
SUBTITLE = font(31)
TAG = font(25, True)
SECTION = font(34, True)
BODY = font(27)
BODY_BOLD = font(27, True)
SMALL = font(23)


def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, fnt, max_width):
    lines = []
    current = ""
    for char in text:
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


def rounded(draw, box, fill, outline=BORDER, radius=28, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, x, y, text, fill):
    pad_x = 22
    pad_y = 8
    w = text_width(draw, text, TAG) + pad_x * 2
    h = 44
    draw.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=fill)
    draw.text((x + pad_x, y + pad_y), text, fill="#ffffff", font=TAG)
    return x + w + 14


def draw_wrapped(draw, text, x, y, max_width, fnt=BODY, fill=INK, line_h=40):
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def draw_bullets(draw, items, x, y, max_width, color, fnt=BODY, line_h=39, gap=17):
    for item in items:
        draw.ellipse((x, y + 12, x + 12, y + 24), fill=color)
        line_y = y
        for line in wrap_text(draw, item, fnt, max_width - 30):
            draw.text((x + 28, line_y), line, font=fnt, fill=INK)
            line_y += line_h
        y = line_y + gap
    return y


def draw_panel(draw, x, y, w, h, title, color):
    rounded(draw, (x, y, x + w, y + h), SURFACE)
    draw.rounded_rectangle((x, y, x + w, y + 76), radius=28, fill=color)
    draw.rectangle((x, y + 42, x + w, y + 76), fill=color)
    draw.text((x + 28, y + 20), title, fill="#ffffff", font=SECTION)
    return x + 32, y + 108, w - 64


def draw_intro_panel(draw, spec, x, y, w, h):
    tx, ty, tw = draw_panel(draw, x, y, w, h, "流派介绍", BLUE)
    ty = draw_wrapped(draw, spec["intro"], tx, ty, tw, BODY, INK, 40)
    ty += 26
    draw.text((tx, ty), "适合场景", fill=BLUE, font=BODY_BOLD)
    ty += 43
    ty = draw_bullets(draw, spec["fit"], tx, ty, tw, BLUE, BODY, 38, 14)
    ty += 4
    draw.text((tx, ty), "核心约束", fill=RED, font=BODY_BOLD)
    ty += 43
    ty = draw_bullets(draw, spec["constraint"], tx, ty, tw, RED, BODY, 38, 14)
    if ty > y + h - 18:
        print(f"warning: intro overflow {spec['file']}")


def draw_metrics_panel(draw, spec, x, y, w, h):
    tx, ty, tw = draw_panel(draw, x, y, w, h, "关注指标", TEAL)
    grouped = spec["metrics"]
    for group_title, items in grouped:
        draw.text((tx, ty), group_title, fill=TEAL, font=BODY_BOLD)
        ty += 43
        ty = draw_bullets(draw, items, tx, ty, tw, TEAL, BODY, 38, 13)
        ty += 6
    if ty > y + h - 18:
        print(f"warning: metrics overflow {spec['file']}")


def draw_stage_card(draw, x, y, w, h, title, color, bullets):
    rounded(draw, (x, y, x + w, y + h), "#fbfcfa", outline=LINE, radius=24)
    draw.rounded_rectangle((x, y, x + w, y + 62), radius=24, fill=color)
    draw.rectangle((x, y + 36, x + w, y + 62), fill=color)
    draw.text((x + 24, y + 16), title, fill="#ffffff", font=BODY_BOLD)
    end_y = draw_bullets(draw, bullets, x + 28, y + 92, w - 56, color, BODY, 39, 16)
    return end_y


def draw_strategy_panel(draw, spec, x, y, w, h):
    tx, ty, tw = draw_panel(draw, x, y, w, h, "详细交易策略", GREEN)
    card_gap = 26
    card_w = (tw - card_gap) // 2
    card_h = (h - 156 - card_gap) // 2
    stages = [
        ("建仓", GREEN, spec["strategy"]["建仓"]),
        ("加仓", TEAL, spec["strategy"]["加仓"]),
        ("止盈/减仓", AMBER, spec["strategy"]["止盈/减仓"]),
        ("止损/退出", RED, spec["strategy"]["止损/退出"]),
    ]
    for idx, (title, color, bullets) in enumerate(stages):
        sx = tx + (idx % 2) * (card_w + card_gap)
        sy = ty + (idx // 2) * (card_h + card_gap)
        end_y = draw_stage_card(draw, sx, sy, card_w, card_h, title, color, bullets)
        if end_y > sy + card_h - 14:
            print(f"warning: strategy overflow {spec['file']} {title}")


def draw_card(spec):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.text((MARGIN, 56), spec["title"], font=TITLE, fill=INK)
    draw.text((MARGIN, 132), spec["subtitle"], font=SUBTITLE, fill=MUTED)
    x = MARGIN
    for label, color in spec["tags"]:
        x = pill(draw, x, 184, label, color)

    left_w = 640
    mid_w = 610
    right_w = WIDTH - MARGIN * 2 - left_w - mid_w - GAP * 2
    top = 260
    main_h = 1160

    draw_intro_panel(draw, spec, MARGIN, top, left_w, main_h)
    draw_metrics_panel(draw, spec, MARGIN + left_w + GAP, top, mid_w, main_h)
    draw_strategy_panel(draw, spec, MARGIN + left_w + mid_w + GAP * 2, top, right_w, main_h)

    footer = "资料用途：建立策略框架，不构成个性化投资建议；执行前应结合资金期限、税费、交易成本、流动性和风险预算。"
    draw.text((MARGIN, HEIGHT - 72), footer, fill=MUTED, font=SMALL)

    image.save(OUT_DIR / spec["file"], quality=95)


SPECS = [
    {
        "file": "passive-index-card.png",
        "title": "被动指数派",
        "subtitle": "用低成本、分散化工具长期持有市场组合，赚市场长期 Beta。",
        "tags": [("收益来源：市场长期上涨", BLUE), ("执行关键词：定投 / 再平衡", GREEN)],
        "intro": "不试图长期预测个股胜负或短期高低点，而是承认市场整体增长和企业盈利扩张带来的长期收益。核心能力不是择时，而是长期纪律、低费用和风险承受。",
        "fit": ["长期资金", "没有时间持续研究个股", "希望降低决策复杂度"],
        "constraint": ["不要把指数当成无风险资产", "下跌时主要检查期限和仓位，而非情绪止损"],
        "metrics": [
            ("产品质量", ["指数覆盖范围", "费用率、跟踪误差", "基金规模和成交流动性"]),
            ("估值与风险", ["指数估值分位", "历史最大回撤", "股债比例和现金需求"]),
            ("执行状态", ["定投是否持续", "实际权重是否偏离目标", "是否需要年度或阈值再平衡"]),
        ],
        "strategy": {
            "建仓": ["先确定投资期限和目标权益仓位", "优先选择低费率、跟踪稳定、流动性充足的宽基基金", "用定投或 3-6 批分步买入，降低一次性择时压力"],
            "加仓": ["按固定周期投入新增资金", "指数回撤且估值分位下降时补充", "权益仓位低于目标区间时通过再平衡补回"],
            "止盈/减仓": ["不因短期浮盈机械卖出", "权益仓位超过目标上限时卖出超配部分", "估值极端偏高或资金期限缩短时降低风险资产比例"],
            "止损/退出": ["一般不做短线价格止损", "基金跟踪失真、规模萎缩或流动性恶化时换产品", "风险承受能力下降或投资目标改变时退出或重设配置"],
        },
    },
    {
        "file": "asset-allocation-card.png",
        "title": "资产配置派",
        "subtitle": "用股票、债券、现金、黄金等资产组合管理收益、波动和回撤。",
        "tags": [("收益来源：大类资产风险溢价", BLUE), ("执行关键词：目标权重 / 再平衡", GREEN)],
        "intro": "资产配置派认为组合的大部分风险和收益来自资产比例，而不是某一只股票。重点是先定义风险预算，再让不同资产在不同环境中分工。",
        "fit": ["中长期家庭资产管理", "需要控制回撤和流动性", "不希望押注单一风格或行业"],
        "constraint": ["相关性在危机中可能上升", "配置比例必须服务资金期限和风险承受"],
        "metrics": [
            ("资产状态", ["股票估值", "债券收益率", "现金收益和流动性", "黄金、商品或 REITs 的配置价值"]),
            ("宏观环境", ["通胀、利率和信用利差", "增长周期和政策方向", "资产间相关性"]),
            ("组合风险", ["目标权重偏离", "组合波动率和最大回撤", "未来 6-24 个月现金需求"]),
        ],
        "strategy": {
            "建仓": ["先设定股票、债券、现金和其他资产的目标比例", "按风险预算分批买入，避免在单一资产上一次性重仓", "保留足够现金覆盖短期支出和再平衡机会"],
            "加仓": ["低配资产回到合理估值时补仓", "某类资产跌到目标权重下限以下时再平衡买入", "宏观环境支持且组合风险未超标时提高目标权重"],
            "止盈/减仓": ["某类资产涨到明显超配时卖出部分", "组合波动或回撤超过预算时降低风险资产", "资产估值极端、风险补偿不足时减仓"],
            "止损/退出": ["不因单一资产短期下跌全盘退出", "资金期限缩短、现金需求提高时重设配置", "风险承受能力下降或配置假设失效时整体降风险"],
        },
    },
    {
        "file": "value-investing-card.png",
        "title": "价值投资派",
        "subtitle": "以低于保守内在价值的价格买入，等待低估修复或经营改善。",
        "tags": [("收益来源：低估修复", BLUE), ("执行关键词：安全边际 / 逻辑止损", GREEN)],
        "intro": "价值投资派相信市场会阶段性错误定价。买入前必须能解释资产为什么便宜、为什么不是陷阱，以及价格回归价值的路径可能是什么。",
        "fit": ["愿意阅读财报和行业资料", "能承受等待期和短期低迷", "偏好赔率明确的买入价格"],
        "constraint": ["便宜不等于低风险", "加仓前必须确认基本面没有继续恶化"],
        "metrics": [
            ("估值", ["PE、PB、EV/EBITDA", "自由现金流收益率", "股息率和资产折价"]),
            ("质量", ["ROE、毛利率和现金流", "资产负债率、净现金和偿债能力", "存货、应收和资本开支"]),
            ("修复证据", ["行业周期位置", "盈利拐点", "管理层治理和资本配置"]),
        ],
        "strategy": {
            "建仓": ["先估算保守内在价值或合理估值区间", "只有折价足以覆盖判断错误时分批买入", "单只标的设置仓位上限，避免价值陷阱拖垮组合"],
            "加仓": ["价格继续下跌但核心基本面未恶化", "盈利、现金流或行业周期出现拐点证据", "折价扩大且资产负债表仍安全时加仓"],
            "止盈/减仓": ["价格接近或超过合理价值时兑现", "折价修复完成但长期增长一般时换仓", "出现更高赔率机会时减仓迁移资金"],
            "止损/退出": ["原估值假设被证伪", "现金流、债务或治理明显恶化", "行业出现永久性衰退或竞争格局不可逆变差"],
        },
    },
    {
        "file": "growth-investing-card.png",
        "title": "成长投资派",
        "subtitle": "为未来高速增长支付溢价，但持续验证增长质量和估值匹配。",
        "tags": [("收益来源：企业成长", BLUE), ("执行关键词：增长兑现 / 估值纪律", GREEN)],
        "intro": "成长投资派买的是未来收入、利润、用户规模或生态扩张。关键不是故事有多大，而是增长能否兑现为现金流和竞争优势。",
        "fit": ["能承受高波动", "愿意跟踪产业和公司数据", "理解估值压缩风险"],
        "constraint": ["高增长必须持续验证", "不要用远期故事掩盖当期经营恶化"],
        "metrics": [
            ("增长", ["收入和利润增速", "用户增长、留存率和 ARPU", "订单、产能、渗透率或份额"]),
            ("质量", ["毛利率和经营杠杆", "单位经济模型", "自由现金流和现金消耗"]),
            ("估值", ["PS、PE、PEG 或 EV/Sales", "市场空间兑现进度", "预期差和竞争格局"]),
        ],
        "strategy": {
            "建仓": ["增长确定性较高且商业模式已被验证", "估值没有把未来多年增长全部透支", "用小仓或分批方式应对高波动"],
            "加仓": ["财报和经营数据连续兑现", "利润率改善或新业务验证成功", "回调后估值重新进入可接受区间"],
            "止盈/减仓": ["增速开始下台阶", "估值显著高于增长可承受范围", "渗透率接近天花板或仓位过度集中"],
            "止损/退出": ["增长逻辑失败或核心客户流失", "毛利率结构性下滑、竞争加剧", "现金消耗失控且融资环境变差"],
        },
    },
    {
        "file": "quality-moat-card.png",
        "title": "质量/护城河派",
        "subtitle": "买长期好生意，关注资本回报、现金流质量和竞争优势。",
        "tags": [("收益来源：优秀企业复利", BLUE), ("执行关键词：合理价格 / 长期持有", GREEN)],
        "intro": "质量派不只问便宜不便宜，更问这是不是一门能长期产生高资本回报的生意。它愿意为确定性付出合理溢价，但不能无视价格。",
        "fit": ["长期资金", "能跟踪公司竞争优势", "希望减少频繁交易"],
        "constraint": ["好公司买太贵也会降低回报", "护城河变弱比短期波动更重要"],
        "metrics": [
            ("商业质量", ["ROE、ROIC 和自由现金流", "毛利率、净利率稳定性", "资产周转和资本开支强度"]),
            ("护城河", ["品牌、渠道和客户粘性", "网络效应或成本优势", "市场份额和定价权"]),
            ("治理与估值", ["管理层资本配置", "负债率和现金储备", "合理 PE、FCF 收益率和预期收益率"]),
        ],
        "strategy": {
            "建仓": ["确认长期竞争优势和现金流质量", "价格进入合理区间时分批买入", "不强求最低点，但要求未来收益率合理"],
            "加仓": ["护城河增强或份额提升", "业绩质量稳定且短期波动带来好价格", "管理层资本配置持续优秀"],
            "止盈/减仓": ["估值极端高、未来收益率明显下降", "单一持仓超过组合上限", "长期逻辑未变但赔率明显变差时降仓"],
            "止损/退出": ["护城河被削弱或替代技术出现", "资本回报率长期下滑", "现金流质量、治理或主业竞争力恶化"],
        },
    },
    {
        "file": "dividend-cashflow-card.png",
        "title": "股息/现金流派",
        "subtitle": "追求可见现金回报，但分红必须由真实现金流支撑。",
        "tags": [("收益来源：分红、利息和租金", BLUE), ("执行关键词：覆盖率 / 稳定性", GREEN)],
        "intro": "股息派不是简单买最高股息率，而是买可持续现金流。真正重要的是分红来源、资产质量和未来分红能力。",
        "fit": ["重视现金收入", "偏好较低决策频率", "组合需要防御性资产"],
        "constraint": ["高股息可能来自股价暴跌", "分红下降会同时打击收益和估值"],
        "metrics": [
            ("现金回报", ["股息率、分红率", "自由现金流覆盖倍数", "派息历史和增长稳定性"]),
            ("资产安全", ["负债率和债务期限", "利息覆盖倍数", "资本开支和监管约束"]),
            ("比较基准", ["债券收益率", "同业股息率", "行业景气和盈利稳定性"]),
        ],
        "strategy": {
            "建仓": ["股息率相对历史和债券收益有吸引力", "分红由自由现金流充分覆盖", "主业稳定、负债和资本开支可控"],
            "加仓": ["股价回落但现金流和分红能力未恶化", "分红安全边际提高", "组合现金回报不足时补充"],
            "止盈/减仓": ["价格上涨导致股息率吸引力下降", "利率环境变化使相对收益不足", "持仓超配时通过再平衡降仓"],
            "止损/退出": ["分红被削减或覆盖率明显恶化", "主业现金流下降、负债再融资压力上升", "资产质量变差导致未来派息不可持续"],
        },
    },
    {
        "file": "trend-momentum-card.png",
        "title": "趋势/动量派",
        "subtitle": "顺着价格趋势试错，用明确止损处理震荡市和假突破。",
        "tags": [("收益来源：趋势延续", BLUE), ("执行关键词：信号 / 止损 / 移动止盈", GREEN)],
        "intro": "趋势派相信市场价格本身包含信息。重点不是猜顶底，而是在趋势形成后跟随，并在趋势证伪时快速退出。",
        "fit": ["能严格执行规则", "能接受连续小亏", "适合有明确交易周期的资金"],
        "constraint": ["震荡市会频繁止损", "加仓只能发生在风险已被压低之后"],
        "metrics": [
            ("趋势信号", ["均线斜率和价格位置", "突破前高或跌破前低", "相对强弱排名"]),
            ("确认信息", ["成交量和波动率", "行业强弱和市场宽度", "回踩是否守住突破位"]),
            ("风险参数", ["ATR 或波动止损距离", "单笔风险占组合比例", "盈亏比和最大连续亏损"]),
        ],
        "strategy": {
            "建仓": ["突破关键区间或站上趋势均线时试仓", "入场前写清止损位和目标位", "单笔亏损限制在预设风险预算内"],
            "加仓": ["突破后回踩不破或再次放量突破", "已有浮盈可保护初始风险", "用金字塔方式逐步加仓并同步上移止损"],
            "止盈/减仓": ["趋势加速过热或相对强度下降", "跌破短期趋势线时减仓", "达到预设风险回报目标后分批兑现"],
            "止损/退出": ["跌破关键均线、前低或突破位", "ATR 止损线被触发", "信号失效时退出，不把交易亏损变成长线持有"],
        },
    },
    {
        "file": "macro-cycle-card.png",
        "title": "宏观/周期派",
        "subtitle": "根据增长、通胀、利率、信用和政策周期切换资产。",
        "tags": [("收益来源：周期切换", BLUE), ("执行关键词：宏观验证 / 资产轮动", GREEN)],
        "intro": "宏观派关注资产在不同经济阶段的相对表现。难点在于方向和节奏都要管理：判断对了但价格已提前反映，也可能亏钱。",
        "fit": ["能跟踪宏观数据和政策", "做资产类别或行业级配置", "理解周期和估值的错位"],
        "constraint": ["宏观叙事必须被数据验证", "不要在赔率不足时追逐共识交易"],
        "metrics": [
            ("宏观数据", ["PMI、CPI、PPI", "就业、消费和投资", "库存周期和企业盈利"]),
            ("金融条件", ["政策利率和收益率曲线", "信用利差、社融或信贷", "汇率和流动性"]),
            ("资产反馈", ["股债商金相对强弱", "估值和风险溢价", "交易拥挤度"]),
        ],
        "strategy": {
            "建仓": ["宏观阶段与资产受益逻辑匹配", "价格尚未充分反映预期", "分批进入受益资产或行业"],
            "加仓": ["宏观数据连续验证同一方向", "政策继续支持或流动性改善", "资产价格仍有风险补偿"],
            "止盈/减仓": ["周期进入下一阶段", "政策边际转向或增长/通胀信号反转", "资产拥挤、估值已充分反映时减仓"],
            "止损/退出": ["核心宏观假设反向变化", "市场走势长期背离且损失超过预算", "相关资产联动失效时降低敞口"],
        },
    },
    {
        "file": "quant-factor-card.png",
        "title": "量化/因子派",
        "subtitle": "用系统规则捕捉价值、动量、质量、低波动等风格溢价。",
        "tags": [("收益来源：统计规律和风格溢价", BLUE), ("执行关键词：模型 / 再平衡 / 风险暴露", GREEN)],
        "intro": "量化因子派把投资决策规则化，追求可回测、可复现、可执行。真正的考验在实盘成本、容量、回撤和模型漂移。",
        "fit": ["有数据和编程能力", "能接受模型阶段性失效", "适合组合化而非单票押注"],
        "constraint": ["回测不等于未来收益", "必须控制交易成本、拥挤和过拟合"],
        "metrics": [
            ("因子质量", ["经济解释和因子暴露", "信息比率和命中率", "跨市场、跨周期稳定性"]),
            ("交易可行性", ["换手率和交易成本", "容量和流动性", "行业、市值和风格偏离"]),
            ("实盘监控", ["最大回撤", "跟踪误差", "数据质量和模型漂移"]),
        ],
        "strategy": {
            "建仓": ["因子有清楚经济解释且不过拟合", "交易成本和容量可承受", "按组合规则分散建仓，不靠主观挑单票"],
            "加仓": ["定期再平衡时恢复目标因子暴露", "模型信号增强且风险预算允许", "不因短期亏损主观摊平"],
            "止盈/减仓": ["因子信号衰减或暴露过高", "组合行业和风格偏离过大", "风险预算或回撤接近上限"],
            "止损/退出": ["实盘回撤超过压力测试", "交易成本显著上升或流动性下降", "数据质量问题、因子拥挤或模型失效"],
        },
    },
    {
        "file": "event-driven-card.png",
        "title": "事件驱动派",
        "subtitle": "围绕并购、重组、回购、分拆等事件，赚概率和价差收敛。",
        "tags": [("收益来源：特殊事件重估", BLUE), ("执行关键词：概率 / 条款 / 时间成本", GREEN)],
        "intro": "事件驱动派不只看公司便宜与否，而是拆解事件能否成功、何时成功、失败损失多大，以及当前价差是否补偿这些风险。",
        "fit": ["能读公告和交易条款", "能跟踪审批和时间表", "能承受事件失败风险"],
        "constraint": ["事件失败损失可能不对称", "资金占用时间会显著影响年化收益"],
        "metrics": [
            ("事件条款", ["并购、重组、回购或指数规则", "价格、换股比例和先决条件", "审批路径和股东投票"]),
            ("概率收益", ["当前价差", "成功概率和失败损失", "预计完成时间和年化收益"]),
            ("风险信号", ["监管态度", "对手方信用", "价格是否暗示失败概率上升"]),
        ],
        "strategy": {
            "建仓": ["事件真实、条款清楚、时间表可跟踪", "预期收益覆盖失败损失和资金成本", "控制单事件仓位，避免黑天鹅集中"],
            "加仓": ["审批、投票或融资进展提高成功率", "价差仍未充分收敛", "失败损失没有扩大且时间成本可接受"],
            "止盈/减仓": ["价差大幅收敛或事件临近落地", "剩余收益率不再覆盖风险", "不确定性上升但尚未失败时先降仓"],
            "止损/退出": ["事件失败、条款变差或审批延迟超预期", "对手方信用恶化", "市场价格持续暗示失败概率上升"],
        },
    },
    {
        "file": "relative-value-arbitrage-card.png",
        "title": "套利/相对价值派",
        "subtitle": "买低估的一边、卖高估的一边，等待价差回归。",
        "tags": [("收益来源：价差收敛", BLUE), ("执行关键词：对冲 / 成本 / 流动性", GREEN)],
        "intro": "相对价值派关注两个相关资产之间的价格偏离。它看起来比方向性下注稳，但真正风险常来自杠杆、流动性、保证金和规则变化。",
        "fit": ["理解交易结构和规则", "能管理保证金和流动性", "适合小心控制杠杆的资金"],
        "constraint": ["套利不等于无风险", "价差扩大时不能无限摊平"],
        "metrics": [
            ("价差信号", ["ETF 折溢价", "期现基差", "利差、配对价差和相关性"]),
            ("执行成本", ["交易成本和冲击成本", "融资利率和保证金", "借券、申赎或交割限制"]),
            ("风险监控", ["回归速度", "流动性深度", "交易规则和极端行情压力"]),
        ],
        "strategy": {
            "建仓": ["价差偏离超过历史区间和交易成本", "存在明确收敛机制或交割路径", "多空或对冲头寸都能真实执行"],
            "加仓": ["价差继续扩大但机制未变", "保证金和流动性充足", "只做有限加仓，不把模型误差放大成杠杆风险"],
            "止盈/减仓": ["价差回归目标区间", "剩余收益无法覆盖资金和交易成本", "资金效率下降时平仓释放额度"],
            "止损/退出": ["收敛机制失效或相关性断裂", "保证金压力上升", "交易规则变化、流动性枯竭或对冲腿失效"],
        },
    },
    {
        "file": "professional-speculation-card.png",
        "title": "专业投机/技术交易派",
        "subtitle": "先定义风险和赔率，再用趋势、反转或假突破信号交易。",
        "tags": [("收益来源：价格波动和赔率", BLUE), ("执行关键词：止损 / 浮盈加仓 / 趋势证伪", GREEN)],
        "intro": "专业投机派不把预测正确放在第一位，而是把风险控制放在第一位。目标是错了小亏、对了放大利润，长期靠纪律和概率生存。",
        "fit": ["能严格执行止损", "能接受连续试错", "适合有明确交易系统的人"],
        "constraint": ["没有止损就不是专业投机", "亏损仓位不能摊平变成长线投资"],
        "metrics": [
            ("信号", ["趋势结构和支撑阻力", "1-2-3 反转", "2B 假突破和成交量确认"]),
            ("风险", ["入场价、止损价和目标价", "ATR、波动率和仓位大小", "单笔亏损占组合比例"]),
            ("系统质量", ["胜率和盈亏比", "最大连续亏损", "执行偏差和复盘记录"]),
        ],
        "strategy": {
            "建仓": ["出现明确交易信号才入场", "入场前计算止损位、目标位和盈亏比", "先小仓试错，单笔亏损不超过预设风险"],
            "加仓": ["只有浮盈足以保护初始风险后加仓", "沿趋势回踩或突破递进加仓", "每次加仓同步上移止损"],
            "止盈/减仓": ["达到目标位或趋势加速衰竭", "出现反向信号或赔率下降", "分批兑现，保留部分仓位跟随大趋势"],
            "止损/退出": ["入场理由失效或价格跌破止损位", "单笔亏损达到上限立即退出", "不取消止损、不摊平亏损、不用希望替代纪律"],
        },
    },
]


def main():
    for spec in SPECS:
        draw_card(spec)
    print(f"generated {len(SPECS)} strategy cards in {OUT_DIR}")


if __name__ == "__main__":
    main()
