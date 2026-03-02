"""AI Agent 主流程：接收用户指令并调度任务。"""

from __future__ import annotations

from .executor import LongTaskHandle, TaskExecutor, sample_stock_action
from .models import TaskRequest
from .planner import TaskPlanner


class AIAgent:
    """面向业务侧的统一入口。"""

    def __init__(self) -> None:
        self._planner = TaskPlanner()
        self._executor = TaskExecutor()

    def handle(self, user_input: str) -> str | LongTaskHandle:
        """处理用户输入并返回执行结果。"""
        task = self._planner.plan(TaskRequest(user_input=user_input))

        # 这里演示统一 action 路由；生产中可接入 Tool Registry 动态分发。
        if "小米" in user_input and "股票" in user_input:
            return self._executor.execute(task, action=sample_stock_action)

        return self._executor.execute(task, action=lambda: f"短任务完成：{task.objective}")

    def active_long_tasks(self) -> int:
        """查询当前运行的长任务数量。"""
        return self._executor.active_jobs()
