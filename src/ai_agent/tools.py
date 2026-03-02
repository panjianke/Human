"""工具层：封装文件修改、网络查询、系统操作等能力。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ToolResult:
    """工具执行结果。"""

    ok: bool
    message: str


class LocalFileTool:
    """本地文件工具：支持按路径写入文本内容。"""

    def write_text(self, path: str, content: str) -> ToolResult:
        """写入文本文件（若目录不存在则自动创建）。"""
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult(ok=True, message=f"已写入文件：{target}")


class WebResearchTool:
    """网络检索工具占位实现。

    说明：生产环境建议接入企业检索代理，统一审计与鉴权。
    """

    def search(self, query: str) -> ToolResult:
        """示例实现：返回提示文本。"""
        return ToolResult(ok=True, message=f"已触发网络检索流程，关键词：{query}")
