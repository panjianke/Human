"""命令行入口，便于本地快速验证。"""

from __future__ import annotations

from .agent import AIAgent
from .executor import LongTaskHandle


def main() -> None:
    """启动交互式命令行。"""
    agent = AIAgent()
    handles: list[LongTaskHandle] = []

    print("AI Agent 已启动，输入 quit 退出，输入 stop 停止所有长任务。")
    while True:
        user_input = input("你> ").strip()
        if user_input == "quit":
            break
        if user_input == "stop":
            for handle in handles:
                handle.stop()
            handles.clear()
            print("已停止所有长任务")
            continue

        result = agent.handle(user_input)
        if isinstance(result, LongTaskHandle):
            handles.append(result)
            print("已创建长任务，请使用 stop 手动停止")
        else:
            print(result)


if __name__ == "__main__":
    main()
