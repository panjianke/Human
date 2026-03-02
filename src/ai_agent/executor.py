"""执行器：负责短任务立即执行，以及长任务循环调度。"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from .models import PlannedTask, TaskType


class LongTaskHandle:
    """长任务控制句柄，用于手动停止。"""

    def __init__(self, stop_func: Callable[[], None]) -> None:
        self._stop_func = stop_func

    def stop(self) -> None:
        """停止长任务。"""
        self._stop_func()


class TaskExecutor:
    """任务执行入口。"""

    def __init__(self) -> None:
        self._jobs: dict[str, threading.Event] = {}

    def execute(self, task: PlannedTask, action: Callable[[], str]) -> str | LongTaskHandle:
        """执行任务。

        - 短任务：执行一次后返回结果。
        - 长任务：后台周期执行并返回可停止句柄。
        """
        if task.task_type == TaskType.SHORT:
            return action()

        if not task.interval_seconds:
            raise ValueError("长任务必须提供 interval_seconds")

        job_id = f"job-{len(self._jobs) + 1}"
        stop_event = threading.Event()
        self._jobs[job_id] = stop_event

        def _loop() -> None:
            while not stop_event.is_set():
                action()
                # 使用 wait 代替 sleep，便于快速停止。
                stop_event.wait(task.interval_seconds)

        thread = threading.Thread(target=_loop, name=job_id, daemon=True)
        thread.start()

        def _stop() -> None:
            stop_event.set()
            self._jobs.pop(job_id, None)

        return LongTaskHandle(stop_func=_stop)

    def active_jobs(self) -> int:
        """当前运行中的长任务数量。"""
        # 清理已经结束的任务（防御性处理）。
        self._jobs = {k: v for k, v in self._jobs.items() if not v.is_set()}
        return len(self._jobs)


def sample_stock_action() -> str:
    """示例长任务动作：生产环境可替换为真实行情 API。"""
    timestamp = int(time.time())
    return f"[{timestamp}] 已获取小米股票价格（示例）"
