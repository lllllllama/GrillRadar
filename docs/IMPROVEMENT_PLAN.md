# GrillRadar 提升计划（External Intelligence & 安全加固）

## 目标
1. **外部信息可信度**：摆脱纯 Mock，改为“可验证的本地数据集 + 高频趋势分析”，支撑 CLI、API 与 Prompt 注入。
2. **多源信息体系完善**：补充关键工程能力（缓存、趋势结构化输出、API 端点），形成闭环的可观测能力。
3. **Web/API 安全加固**：默认启用速率限制、输入守卫与结构化日志，降低直接部署到公网时的风控成本。

## 路线图
### 1. External Intelligence 体系
- 引入 `LocalDatasetProvider`（JSON 真数据 + 关键字频次 + 主题趋势），并通过 `ExternalInfoService` 的 `provider_type=local_dataset` 激活。
- 扩展 `ExternalInfoSummary`，新增 `keyword_trends`、`topic_trends` 等字段，供 Prompt、API 与 Web 端消费。
- 在 API (`/external-info/trends`) 和 Prompt Builder 中提供结构化的趋势提示，确保生成的问题能够引用真实趋势。

### 2. 多源爬虫工程补足
- 为多源提供者增加本地缓存、趋势聚合与容错日志，避免线程池结果丢失；
- 将 Trend 数据暴露给 CLI/API，便于可观测和离线评估。

### 3. Web/API 安全
- 新增 `RateLimiterMiddleware`（令牌桶/滑动窗口）限制每 IP 的请求速率，默认 60 秒 30 次，可通过环境变量调整；
- 所有 API 日志追加 `request_id` 与限流命中记录，方便审计。

## 交付物
- `docs/IMPROVEMENT_PLAN.md`（本文）
- `ExternalInfoSummary` / Provider / API / Prompt 的代码更新
- 新增测试覆盖（本地数据提供者、趋势结构、限流命中）
- 通过 `pytest` 回归
