# LangChain Task Agent（短任务 / 长任务）

这是一个面向企业场景的 AI Agent 基础工程，核心目标：
- **短任务**：执行即结束（如“修改一下本地文件”）。
- **长任务**：按周期持续执行，需手动停止（如“每小时给我发送小米股票价格信息”）。
- **真实能力**：支持电脑命令执行、联网检索、行情获取与 webhook 推送。

## 架构设计

- `TaskPlanner`：负责将自然语言解析为任务结构（短任务/长任务、周期等）。
- `TaskExecutor`：负责任务执行与长任务生命周期管理。
- `Tools`：
  - `ComputerControlTool`：执行本地命令
  - `LocalFileTool`：写本地文件
  - `WebResearchTool`：联网检索（DuckDuckGo API）
  - `StockPriceTool`：行情查询（Stooq）
  - `NotificationTool`：推送到 webhook
- `AIAgent`：统一编排入口。

## 企业规范建议

1. **权限最小化**：工具层按能力分级授权（命令执行建议白名单）。
2. **审计追踪**：所有任务输入、执行步骤、结果均落审计日志。
3. **人工确认**：涉及系统级变更时增加二次确认。
4. **停止机制**：长任务必须可追踪、可手动停止。
5. **可观测性**：接入日志、指标、告警（如 Prometheus + Grafana）。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
python -m ai_agent.cli
```

## 命令示例

> 当前 CLI 为演示版，推荐使用下列格式触发真实工具能力。

- 执行电脑命令：`执行命令: pwd`
- 写本地文件：`写文件:/tmp/demo.txt|hello`
- 联网检索：`搜索: LangChain agent best practices`
- 长任务行情提醒：`每小时给我发送小米股票价格信息`

## 行情推送配置

若需自动推送，配置环境变量：

```bash
export AGENT_WEBHOOK_URL="https://your-webhook-endpoint"
```

当触发小米股票任务时，Agent 会先获取 `1810.hk` 行情，再推送消息到该 webhook。

## 下一步扩展

- 将 `TaskPlanner` 替换为 LangChain 结构化输出（JSON schema）。
- 接入企业 IM（飞书/钉钉）与多渠道通知路由。
- 为“操作用户电脑”能力加入沙箱执行与高风险命令拦截。
