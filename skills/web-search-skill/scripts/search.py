"""
scripts/search.py — Google 批量搜索（Serper）

完整复刻 search MCP server 的输入处理逻辑：
  - 批量 API 一次请求多个 query
  - snippet 优先级：extra_snippets > snippet > description
  - 自动 retry（最多 3 次），最后一次尝试去除引号重试
  - 输出格式与 MCP server 完全一致

环境变量：
  SERPER_API_KEY  （必须）

输入：
  queries   list[str]   搜索词列表，支持 Google 高级搜索语法

输出（str）：
  --- search result for [query] ---
  <title>...</title>
  <url>...</url>
  <snippet>...</snippet>
  --- end of search result ---

用法：
  CLI:    python scripts/search.py "Claude AI" "LLM inference"
  import: from scripts.search import search; result = search(["Claude AI"])
"""

import os
import sys
import time
import random
import logging
from typing import Any

import httpx

logger = logging.getLogger("search")

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
MAX_RETRY = 3


# ──────────────────────────────────────────────
# 内部函数
# ──────────────────────────────────────────────

def _batch_search(queries: list[str]) -> list[list[dict[str, Any]]]:
    """一次 API 调用批量搜索多个 query，返回每条 query 的 organic 结果列表。"""
    payload = [{"q": q, "num": 10} for q in queries]
    with httpx.Client(timeout=300.0) as client:
        resp = client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json=payload,
        )
    resp.raise_for_status()
    results = resp.json()
    if not isinstance(results, list):
        raise ValueError(f"Unexpected response format: expected list, got {type(results)}")
    return [r.get("organic", []) for r in results]


def _get_brief_text(contents: list[dict[str, Any]]) -> str:
    """从 organic 结果提取摘要文本，优先级：extra_snippets > snippet > description。"""
    parts = []
    for item in contents:
        if item.get("extra_snippets"):
            snippet = "\n".join(item["extra_snippets"])
        elif item.get("snippet"):
            snippet = item["snippet"]
        else:
            snippet = item.get("description", "")
        url = item.get("url") or item.get("link", "")
        parts.append(
            f"<title>{item['title']}</title>\n"
            f"<url>{url}</url>\n"
            f"<snippet>\n{snippet}\n</snippet>"
        )
    return "\n\n".join(parts)


def _format_output(queries: list[str], results: list[str]) -> str:
    lines = []
    for q, r in zip(queries, results):
        lines.append(f"--- search result for [{q}] ---\n{r}\n--- end of search result ---")
    return "\n\n".join(lines)


# ──────────────────────────────────────────────
# 公开接口
# ──────────────────────────────────────────────

def search(queries: list[str]) -> str:
    """
    批量 Google 搜索。

    Args:
        queries: 搜索词列表，支持 Google 高级语法（site:、intitle: 等）

    Returns:
        格式化字符串，每条 query 对应一块结果
    """
    queries = [q for q in queries if q.strip()]
    if not queries:
        return ""

    if not SERPER_API_KEY:
        return "Error: SERPER_API_KEY not configured."

    empty_result = "Search result is empty. Please try with more general and valid queries."

    for retry in range(MAX_RETRY):
        try:
            batch = _batch_search(queries)
            results = []
            for i, q in enumerate(queries):
                text = _get_brief_text(batch[i]) if i < len(batch) else ""
                results.append(text if text else empty_result)
            return _format_output(queries, results)

        except Exception as e:
            if any(w in str(e).lower() for w in ["client error", "403", "denied"]):
                logger.error(f"Serper access denied: {e}")
                return "Searching for these queries is denied. Please try more general and valid queries."

            logger.warning(f"Search attempt {retry + 1}/{MAX_RETRY} failed: {e}")
            time.sleep(random.uniform(1, 16))

            # 最后一次：尝试去除引号重试
            if retry == MAX_RETRY - 1:
                cleaned = [q.replace('"', '') for q in queries]
                if cleaned != queries:
                    try:
                        batch = _batch_search(cleaned)
                        results = []
                        for i, orig_q in enumerate(queries):
                            text = _get_brief_text(batch[i]) if i < len(batch) else ""
                            if not text:
                                results.append(empty_result)
                            elif '"' in orig_q:
                                results.append(
                                    f"Search result for [{orig_q}] is empty. "
                                    f"Returning result for cleaned query instead.\n\n{text}"
                                )
                            else:
                                results.append(text)
                        return _format_output(queries, results)
                    except Exception:
                        pass

                return _format_output(queries, [empty_result] * len(queries))


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    queries = sys.argv[1:]
    if not queries:
        print("用法: python search.py <query1> [query2 ...]", file=sys.stderr)
        sys.exit(1)
    print(search(queries))