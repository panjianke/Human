"""工具层：封装电脑操作、联网检索与行情推送能力。"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shlex
import subprocess
from typing import Any
from urllib import parse, request


@dataclass(slots=True)
class ToolResult:
    """工具执行结果。"""

    ok: bool
    message: str
    data: dict[str, Any] | None = None


class LocalFileTool:
    """本地文件工具：支持按路径写入文本内容。"""

    def write_text(self, path: str, content: str) -> ToolResult:
        """写入文本文件（若目录不存在则自动创建）。"""
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult(ok=True, message=f"已写入文件：{target}", data={"path": str(target)})


class ComputerControlTool:
    """电脑操作工具：执行受控命令。"""

    def run_command(self, command: str, timeout_seconds: int = 30) -> ToolResult:
        """执行本地命令并返回结果。

        说明：使用 shlex 解析避免直接 shell 注入；生产环境建议进一步增加命令白名单。
        """
        try:
            args = shlex.split(command)
            if not args:
                return ToolResult(ok=False, message="命令为空")

            completed = subprocess.run(  # noqa: S603
                args,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return ToolResult(
                ok=completed.returncode == 0,
                message="命令执行完成",
                data={
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                    "returncode": completed.returncode,
                },
            )
        except FileNotFoundError:
            return ToolResult(ok=False, message="命令不存在")
        except subprocess.TimeoutExpired:
            return ToolResult(ok=False, message=f"命令超时（>{timeout_seconds}s）")


class WebResearchTool:
    """联网检索工具：使用 DuckDuckGo Instant Answer API。"""

    _ENDPOINT = "https://api.duckduckgo.com/"

    def search(self, query: str, max_results: int = 5) -> ToolResult:
        """联网检索并返回摘要结果。"""
        params = parse.urlencode(
            {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
            }
        )
        url = f"{self._ENDPOINT}?{params}"
        try:
            payload = self._http_get_json(url)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(ok=False, message=f"检索失败：{exc}")

        results: list[dict[str, str]] = []
        abstract = payload.get("AbstractText")
        if abstract:
            results.append({"title": payload.get("Heading", "摘要"), "snippet": abstract})

        related = payload.get("RelatedTopics", [])
        for item in related:
            if len(results) >= max_results:
                break
            if "Text" in item:
                results.append({"title": item.get("FirstURL", "相关结果"), "snippet": item["Text"]})
            elif "Topics" in item:
                for sub in item.get("Topics", []):
                    if len(results) >= max_results:
                        break
                    if "Text" in sub:
                        results.append({"title": sub.get("FirstURL", "相关结果"), "snippet": sub["Text"]})

        return ToolResult(ok=True, message=f"检索完成，共 {len(results)} 条", data={"results": results})

    @staticmethod
    def _http_get_json(url: str) -> dict[str, Any]:
        """发起 GET 请求并解析 JSON。"""
        with request.urlopen(url, timeout=15) as response:  # noqa: S310
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset))


class StockPriceTool:
    """行情工具：从 Stooq 获取公开股票价格。"""

    _ENDPOINT = "https://stooq.com/q/l/"

    def get_price(self, symbol: str) -> ToolResult:
        """查询股票价格。

        symbol 示例：`1810.hk`（小米）。
        """
        params = parse.urlencode({"s": symbol.lower(), "i": "d"})
        url = f"{self._ENDPOINT}?{params}"
        try:
            with request.urlopen(url, timeout=15) as response:  # noqa: S310
                text = response.read().decode("utf-8").strip()
        except Exception as exc:  # noqa: BLE001
            return ToolResult(ok=False, message=f"行情获取失败：{exc}")

        lines = [line for line in text.splitlines() if line]
        if len(lines) < 2:
            return ToolResult(ok=False, message="行情响应格式异常")

        headers = [h.strip().lower() for h in lines[0].split(",")]
        values = [v.strip() for v in lines[1].split(",")]
        row = dict(zip(headers, values, strict=False))
        close_price = row.get("close")
        if not close_price or close_price.upper() == "N/D":
            return ToolResult(ok=False, message=f"未获取到 {symbol} 的有效价格")

        return ToolResult(
            ok=True,
            message=f"{symbol} 最新收盘价：{close_price}",
            data={"symbol": symbol, "close": close_price, "date": row.get("date")},
        )


class NotificationTool:
    """推送工具：向 Webhook 发送消息。"""

    def push_webhook(self, webhook_url: str, message: str) -> ToolResult:
        """推送文本消息到 webhook。"""
        payload = json.dumps({"text": message}).encode("utf-8")
        req = request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15) as response:  # noqa: S310
                status = response.status
        except Exception as exc:  # noqa: BLE001
            return ToolResult(ok=False, message=f"推送失败：{exc}")

        if 200 <= status < 300:
            return ToolResult(ok=True, message="推送成功")
        return ToolResult(ok=False, message=f"推送失败，状态码：{status}")
