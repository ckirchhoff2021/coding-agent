"""内置工具：在 deepagents 默认 Shell/文件工具基础上补充可选的网络搜索。

注意：deepagents 的 LocalShellBackend 默认已注入
execute / read_file / write_file / edit_file / ls / glob /grep / write_todos / task
等核心工具，无需重复注册。
本模块只补充 deepagents 没内置但通用的能力（如 web 搜索），按需 gracefully 降级。
"""

from __future__ import annotations

import os
from typing import Any


def _try_tavily() -> list[Any]:
    """若安装了 tavily-python 且配置了 TAVILY_API_KEY，返回搜索工具；否则返回空列表。"""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return []
    try:
        from langchain_community.tools import TavilySearchResults
        return [TavilySearchResults(max_results=5, api_key=api_key)]
    except Exception:
        return []


def _try_tavily_direct() -> list[Any]:
    """备用：直接用 tavily-python SDK。"""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return []
    try:
        from tavily import TavilyClient
        from langchain_core.tools import tool

        client = TavilyClient(api_key=api_key)

        @tool
        def web_search(query: str, max_results: int = 5) -> str:
            """搜索互联网获取最新信息。输入查询词，返回相关网页标题+URL+摘要。"""
            r = client.search(query, max_results=max_results)
            lines = []
            for i, item in enumerate(r.get("results", []), 1):
                lines.append(f"[{i}] {item.get('title','')}\n    URL: {item.get('url','')}\n    {item.get('content','')[:300]}")
            return "\n\n".join(lines) if lines else "(无结果)"

        return [web_search]
    except Exception:
        return []


def get_builtin_tools() -> list[Any]:
    """返回内置附加工具列表（不含 deepagents 默认注入的 Shell/文件/待办/委派工具）。"""
    tools: list[Any] = []
    tools.extend(_try_tavily())
    if not tools:
        tools.extend(_try_tavily_direct())
    return tools
