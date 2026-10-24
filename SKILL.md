---
name: amap-lead-keyword-planner
description: 将公司介绍、产品说明、招商方案或业务模式转换为可在高德地图等地图软件中检索的 B 端行业关键词，最终交付包含业务摘要及 priority_1、priority_2、priority_3 三个工作表的 Excel，并给出匹配逻辑、市场规模和趋势。用户提到“地图获客关键词”“高德扫客行业词”“根据业务介绍生成行业关键词”“按 skill v1.2.0 schema 输出”“线索优先级”“关键词 market_size/trend”“输出 Excel”或需要为地图拓客、广告定投、招商获客生成结构化行业清单时使用。
---

# 地图获客行业关键词分析

把业务资料转成可检索、可分级的行业关键词，最终交付 `.xlsx`。JSON 只作为生成与校验的中间格式，不作为最终交付物；除非用户明确要求，不要输出大段 JSON、Markdown 表格或来源说明代替 Excel。

## 执行流程

1. 提取业务事实：产品/服务、核心功能、直接客户、渠道客户、付费能力、地域属性、复购或持续充值可能性。只使用输入可支持的事实，不补造资质、价格或效果。
2. 生成候选词：同时覆盖服务商/渠道商、直接使用者、相邻潜在行业。每个词必须通过“地图检索能否返回一批同类实体公司或门店”的检验。
3. 核实市场信息：搜索当前行业规模与趋势，优先官方统计、行业协会、上市公司资料和研究机构。详细规则见 [references/ranking-guide.md](references/ranking-guide.md)。
4. 分为三级：默认 `priority_1` 16 条、`priority_2` 20 条、`priority_3` 20 条。用户指定数量或分配时以用户要求为准。
5. 按 [references/output-contract.md](references/output-contract.md) 生成中间 JSON，保持 v1.2.0 字段结构不变。
6. 交付前校验中间 JSON；默认数量测试加 `--require-default-counts`：

```bash
python3 scripts/validate_output.py result.json --require-default-counts
```

7. 校验通过后导出 Excel；使用外部资料时同时传入来源文件：

```bash
python3 scripts/export_excel.py result.json 地图获客行业关键词.xlsx --sources sources.json
```

校验或导出失败时修正后重新执行，不把未通过的结果交给用户。Excel 需通过工作簿验证后再交付。

## 关键词规则

- 使用常见企业/门店类型词，如“广告公司”“装修公司”“口腔门诊”，不要使用抽象需求、动作、产品名或人群概念。
- 优先选择能直接复制进地图搜索框的短词；生僻全称、长句和带修饰语的词要改成常用检索词。
- 全部关键词不得重复。近义词只有在地图检索结果和商业含义确实不同的时候才同时保留。
- `logic` 写清“为什么匹配 + 自用/代理/渠道机会”，避免只复述行业定义。
- `market_size` 有可靠数字时写“规模 + 年份/口径”；没有可靠数字时写定性规模，禁止编数字。
- `trend` 以“上涨 / 温和上涨 / 结构性分化 / 下行”之一开头，可在其后用逗号补一句简短原因。

## 输出纪律

- 最终交付一个 `.xlsx`：包含 `business_summary`、`priority_1`、`priority_2`、`priority_3`；使用外部资料时增加 `资料来源`。
- 三个优先级工作表只保留四列：`keyword`、`logic`、`market_size`、`trend`。
- 工作表需冻结表头、启用筛选、设置合适列宽，并对长文本自动换行。
- 中间 JSON 顶层只保留 `business_summary`、`priority_1`、`priority_2`、`priority_3`；每个关键词对象只保留四个规定字段。
- 中间 JSON 必须合法：使用双引号，不写尾逗号，不包代码围栏，不添加评分字段。
- 市场数据无法核实时宁可定性，不伪造精确数字、年份或来源；外部数据在 `资料来源` 页记录来源名称和 URL。
- 需要查看精简输入输出示例时读 [references/example-imai.md](references/example-imai.md)；机器可读中间 Schema 见 [references/output-schema.json](references/output-schema.json)。
