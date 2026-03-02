from ai_agent.tools import ComputerControlTool, StockPriceTool, ToolResult, WebResearchTool


def test_computer_control_tool_run_command() -> None:
    tool = ComputerControlTool()
    result = tool.run_command("echo hello")
    assert result.ok is True
    assert result.data is not None
    assert result.data["stdout"] == "hello"


def test_web_research_tool_parse_results(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    tool = WebResearchTool()

    def fake_http_get_json(url: str):
        assert "duckduckgo" in url
        return {
            "Heading": "LangChain",
            "AbstractText": "LangChain 是一个构建大模型应用的框架。",
            "RelatedTopics": [{"Text": "LangGraph 是其编排框架", "FirstURL": "https://example.com"}],
        }

    monkeypatch.setattr(tool, "_http_get_json", fake_http_get_json)
    result = tool.search("LangChain")
    assert result.ok is True
    assert result.data is not None
    assert len(result.data["results"]) >= 1


def test_stock_price_tool_parse_csv(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    tool = StockPriceTool()

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"Symbol,Date,Time,Open,High,Low,Close,Volume\n1810.HK,2026-01-01,16:00:00,12,13,11,12.5,1000"

    monkeypatch.setattr("ai_agent.tools.request.urlopen", lambda *args, **kwargs: DummyResponse())
    result = tool.get_price("1810.hk")
    assert result.ok is True
    assert result.data is not None
    assert result.data["close"] == "12.5"


def test_tool_result_shape() -> None:
    result = ToolResult(ok=True, message="ok", data={"a": 1})
    assert result.ok is True
    assert result.data == {"a": 1}
