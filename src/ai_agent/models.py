"""核心数据模型定义。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskType(str, Enum):
    """任务类型枚举。"""

    SHORT = "short"
    LONG = "long"


@dataclass(slots=True)
class TaskRequest:
    """用户任务请求。"""

    user_input: str


@dataclass(slots=True)
class PlannedTask:
    """规划后的任务结构。"""

    task_type: TaskType
    objective: str
    interval_seconds: int | None = None
    require_manual_stop: bool = False
