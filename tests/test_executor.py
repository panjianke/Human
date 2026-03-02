import time

from ai_agent.executor import TaskExecutor
from ai_agent.models import PlannedTask, TaskType


def test_long_task_can_stop() -> None:
    executor = TaskExecutor()
    calls = {"n": 0}

    def action() -> str:
        calls["n"] += 1
        return "ok"

    handle = executor.execute(
        PlannedTask(
            task_type=TaskType.LONG,
            objective="test",
            interval_seconds=1,
            require_manual_stop=True,
        ),
        action=action,
    )

    time.sleep(1.2)
    handle.stop()  # type: ignore[attr-defined]
    active = executor.active_jobs()

    assert calls["n"] >= 1
    assert active == 0
