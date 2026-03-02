from ai_agent.models import TaskRequest, TaskType
from ai_agent.planner import TaskPlanner


def test_short_task() -> None:
    planner = TaskPlanner()
    task = planner.plan(TaskRequest(user_input="修改一下本地文件"))
    assert task.task_type == TaskType.SHORT
    assert task.require_manual_stop is False


def test_long_task_hourly() -> None:
    planner = TaskPlanner()
    task = planner.plan(TaskRequest(user_input="每小时给我发送小米股票价格信息"))
    assert task.task_type == TaskType.LONG
    assert task.interval_seconds == 3600
    assert task.require_manual_stop is True
