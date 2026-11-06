## 1. 内容

- [x] 1.1 补充结构术语与相关方法、固定分析流程
- [x] 1.2 保存原图并编写黄金周线案例及证据边界
- [x] 1.3 接入 README、术语表和策略文档导航

## 2. 验证

- [x] 2.1 核对公式例子、Markdown 链接和结构、原图哈希与解码
- [x] 2.2 通过 change 严格校验和 `git diff --check`
- [x] 2.3 完成内容审查与归档准备

## 验证记录

- 9 份 Markdown、61 个本地引用通过检查；表格列数、代码围栏和行尾空白通过检查。
- 看涨／看跌 FVG 边界与中点、区间中点、合约风险换算、收盘与影线示例通过算术核对。
- PNG 可解码，尺寸 1830×880；复制前后 SHA256 一致：`e3dcd55c9090e5180ce99a72b5bf90811bd3aada895428f7b3607d40567f060d`。
- CLI 通过 `npm exec --yes --package=@fission-ai/openspec@1.14.1 -- openspec ...` 调用；change 严格校验与 `git diff --check` 通过。
- 已审查截图报价、未知时刻、未收盘、区域估读和缺失量价证据的边界。本次无 HTML/JS 或人口数据变更。
- 已归档为 `2026-11-03-add-market-structure-analysis`，同步 3 条新增要求；主规格 `beginner-investment-education` 严格校验通过，归档后 `git diff --check` 通过。
