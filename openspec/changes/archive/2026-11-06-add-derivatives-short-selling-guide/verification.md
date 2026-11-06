# 验证记录

日期：2026-11-06。

## 已完成

- 检查 6 份本次新增或修改的学习文档，84 个相对链接／锚点、49 处参考链接使用均能解析；新增文档的 Markdown 表格列数、代码围栏配对通过。
- Python 独立复算 Put 到期表、熊市看跌价差表、两手 MNQ 盈亏表、Delta/Gamma 和 IV 影响例子、追保缓冲、恢复初始保证金及费用预算，结果符合正文。
- Black–Scholes 在 S=23、K=25、sigma=0.5、T=7/365、r=q=0 下，Delta=0.1210857910，对冲股数=121085.7910，解释约 12.1 万股。
- 官方资料复核包括 OIC、SEC、FINRA、Nasdaq、CME、NFA、富途与长桥香港；未获取的富途 MNQ 保证金及长桥 MNQ 支持状态均保留明确缺口。富途综合账户口径标注为官方检索摘要且需再次核对账户。
- OpenSpec change 严格校验通过；git diff --check 通过。
- 本次仅 Markdown 文档，无网页、JS、数据映射或依赖变更，因此 UI／人口数据测试不适用。
- 既有市场结构指南、黄金截图案例和导航修改保留；未暂存、提交或推送任何文件。

## 归档合并范围

仅向 beginner-investment-education 追加 5 条 requirement，不修改或删除已有 requirement。按仓库规定使用 openspec archive --yes 同步并归档；归档后复核主规格。

## 归档后结果

- `openspec archive add-derivatives-short-selling-guide --yes` 完成，新增 5 条、修改 0 条、删除 0 条；归档目录为 2026-11-06-add-derivatives-short-selling-guide。
- `openspec validate beginner-investment-education --type spec --strict --no-interactive` 通过。
- 最终检查 84 个相对链接／锚点、49 处参考链接使用、168 行表格，均通过；新增价格冲击例子及费用最小跳动计算通过。
- 市场结构与黄金案例的已有要求及文件保留，工作区保持未提交状态。
