"""AI Agent 主流程：接收用户指令并调度任务。"""

from __future__ import annotations

import os
from typing import Callable

from .executor import LongTaskHandle, TaskExecutor
from .models import TaskRequest
from .planner import TaskPlanner
from .tools import ComputerControlTool, LocalFileTool, NotificationTool, StockPriceTool, WebResearchTool


class AIAgent:
    """面向业务侧的统一入口。"""

    def __init__(self) -> None:
        self._planner = TaskPlanner()
        self._executor = TaskExecutor()
        self._computer_tool = ComputerControlTool()
        self._file_tool = LocalFileTool()
        self._web_tool = WebResearchTool()
        self._stock_tool = StockPriceTool()
        self._push_tool = NotificationTool()

    def handle(self, user_input: str) -> str | LongTaskHandle:
        """处理用户输入并返回执行结果。"""
        task = self._planner.plan(TaskRequest(user_input=user_input))
        action = self._route_action(user_input)
        result = self._executor.execute(task, action=action)

        if isinstance(result, LongTaskHandle):
            return result
        return result

    def _route_action(self, user_input: str) -> Callable[[], str]:
        """根据输入进行工具路由。"""
        text = user_input.strip()

        if text.startswith("执行命令:"):
            command = text.split(":", 1)[1].strip()

            def _action() -> str:
                result = self._computer_tool.run_command(command)
                return self._format_tool_result(result)

            return _action

        if text.startswith("写文件:"):
            # 格式：写文件:/tmp/a.txt|内容
            payload = text.split(":", 1)[1]
            path, content = payload.split("|", 1)

            def _action() -> str:
                result = self._file_tool.write_text(path.strip(), content)
                return self._format_tool_result(result)

            return _action

        if text.startswith("搜索:") or text.startswith("检索:"):
            query = text.split(":", 1)[1].strip()

            def _action() -> str:
                result = self._web_tool.search(query)
                return self._format_tool_result(result)

            return _action

        if "小米" in text and "股票" in text:

            def _action() -> str:
                quote = self._stock_tool.get_price("1810.hk")
                if not quote.ok:
                    return quote.message

                message = f"小米当前价格提醒：{quote.message}"
                webhook = os.getenv("AGENT_WEBHOOK_URL", "")
                if webhook:
                    push_result = self._push_tool.push_webhook(webhook, message)
                    return f"{message}；推送结果：{push_result.message}"
                return f"{message}；未配置 AGENT_WEBHOOK_URL，跳过推送"

            return _action

        return lambda: f"短任务完成：{text}"

    @staticmethod
    def _format_tool_result(result: object) -> str:
        """统一格式化工具执行结果。"""
        if hasattr(result, "ok") and hasattr(result, "message"):
            return f"[{ '成功' if result.ok else '失败' }] {result.message}"  # type: ignore[attr-defined]
        return str(result)

    def active_long_tasks(self) -> int:
        """查询当前运行的长任务数量。"""
        return self._executor.active_jobs()
