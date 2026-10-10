## 1. 内容与入口

- [x] 1.1 新增分类术语、核心指标解释和数据口径说明
- [x] 1.2 补充虚构计算案例、假突破案例、自测与官方来源
- [x] 1.3 在 README、基础术语表和策略文档加入阅读入口

## 2. 验证与收尾

- [x] 2.1 核对 Markdown 结构、相对链接与案例算术
- [x] 2.2 运行 `git diff --check` 与 change 严格校验
- [x] 2.3 完成实施任务并确认满足归档条件

## 验证记录

- 8 份 Markdown 的本地链接、代码围栏和空白检查通过；新教材表格列数一致。
- 17 项案例算术复核通过，涵盖 K 线、均线、MACD、RSI、KDJ、ATR、仓位与期望。
- `git diff --check` 与 change 严格校验通过。
- 环境未在 PATH 提供 `openspec`，通过 `npm exec --yes --package=@fission-ai/openspec -- openspec ...` 执行 CLI（1.14.1）；没有向仓库添加依赖。
- 已归档并同步 3 条主规格要求；新 CLI 的严格校验发现主规格既有 Purpose 占位文字，已补充真实用途说明后重新校验。
- 本次仅修改 Markdown 内容、链接和规格，没有 HTML/JS 或人口数据变更。
