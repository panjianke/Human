from ai_agent.agent import AIAgent
from ai_agent.tools import ToolResult


def test_agent_search_route(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    agent = AIAgent()

    monkeypatch.setattr(agent._web_tool, "search", lambda q: ToolResult(ok=True, message=f"已检索 {q}"))
    result = agent.handle("搜索: LangChain")
    assert isinstance(result, str)
    assert "成功" in result


def test_agent_stock_route_without_webhook(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    agent = AIAgent()
    monkeypatch.setattr(agent._stock_tool, "get_price", lambda s: ToolResult(ok=True, message="1810.hk 最新收盘价：12.5"))
    result = agent.handle("查询小米股票价格")
    assert isinstance(result, str)
    assert "未配置 AGENT_WEBHOOK_URL" in result
