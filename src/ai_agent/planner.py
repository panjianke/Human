"""任务规划器：将自然语言请求拆分为短任务/长任务。"""

from __future__ import annotations

import re
from typing import Protocol

from .models import PlannedTask, TaskRequest, TaskType


class LLMPlanner(Protocol):
    """可选的 LangChain 规划接口，便于替换不同大模型。"""

    def invoke(self, prompt: str) -> str:  # pragma: no cover - 具体实现由外部注入
        """调用模型返回文本结果。"""


class TaskPlanner:
    """基于规则 + 可选 LLM 的任务规划器。"""

    def __init__(self, llm_planner: LLMPlanner | None = None) -> None:
        self._llm_planner = llm_planner

    def plan(self, request: TaskRequest) -> PlannedTask:
        """规划任务类型与执行参数。"""
        text = request.user_input.strip()
        interval = self._extract_interval_seconds(text)
        if interval is not None:
            return PlannedTask(
                task_type=TaskType.LONG,
                objective=text,
                interval_seconds=interval,
                require_manual_stop=True,
            )

        # 默认判定为短任务，执行后自动结束。
        return PlannedTask(
            task_type=TaskType.SHORT,
            objective=text,
            require_manual_stop=False,
        )

    @staticmethod
    def _extract_interval_seconds(text: str) -> int | None:
        """解析长任务时间表达式，目前支持“每小时/每N分钟/每N秒”。"""
        normalized = text.replace(" ", "")
        if "每小时" in normalized:
            return 3600

        minute_match = re.search(r"每(\d+)分钟", normalized)
        if minute_match:
            return int(minute_match.group(1)) * 60

        second_match = re.search(r"每(\d+)秒", normalized)
        if second_match:
            return int(second_match.group(1))

        return None
