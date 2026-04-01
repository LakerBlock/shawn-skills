"""
scripts/fetch.py — 网页内容抓取（Jina）+ LLM 摘要（Browse Model）

完整复刻 browse MCP server 的输入处理逻辑：
  - 多 URL 并发处理（ThreadPoolExecutor）
  - Jina 抓取带 retry + random sleep + 403/denied 特判
  - LLM 分析带 retry；内容超 120k tokens 自动分块并发
  - 输出格式与 MCP server 完全一致

环境变量：
  JINA_API_KEY      （必须）
  BROWSE_MODEL      （必须）
  BROWSE_BASE_URL   （必须，回退 BROWSE_API_BASE，默认 http://localhost:4000）
  BROWSE_API_KEY    （必须）

输入：
  urls          list[str]   待抓取的 URL 列表
  browse_query  str         想从页面获取什么（可选，默认全文摘要）

输出（str）：
  --- answer based on [url] ---
  LLM 提炼后的答案...
  --- end of answer ---

用法：
  CLI:    python scripts/fetch.py https://example.com "核心观点是什么？"
          python scripts/fetch.py https://a.com https://b.com "今日新闻"
  import: from scripts.fetch import fetch; result = fetch(["https://example.com"], "核心观点")
"""

import os
import sys
import re
import time
import math
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
import tiktoken
from openai import OpenAI

logger = logging.getLogger("fetch")

# ── 环境变量 ──────────────────────────────────
JINA_API_KEY    = os.getenv("JINA_API_KEY", "")
BROWSE_MODEL    = os.getenv("BROWSE_MODEL", "")
BROWSE_BASE_URL = (os.getenv("BROWSE_BASE_URL")
                   or os.getenv("BROWSE_API_BASE")
                   or "http://localhost:4000")
BROWSE_API_KEY  = os.getenv("BROWSE_API_KEY", "")

TOKEN_LIMIT = 120000
MAX_RETRY   = 3

# ── LLM 客户端 ────────────────────────────────
_client = None
if BROWSE_API_KEY and BROWSE_BASE_URL:
    _client = OpenAI(api_key=BROWSE_API_KEY, base_url=BROWSE_BASE_URL)


# ──────────────────────────────────────────────
# Step 1：LLM 单次请求
# ──────────────────────────────────────────────

def _get_response(prompt: str, max_retry: int = 2) -> str | None:
    """调用 BROWSE_MODEL，失败时按指数退避重试。"""
    if not _client:
        logger.error("OpenAI client not initialized")
        return None
    for attempt in range(max_retry):
        try:
            resp = _client.chat.completions.create(
                model=BROWSE_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=24000,
            )
            text = resp.choices[0].message.content or ""
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
            return text
        except Exception as e:
            logger.warning(f"LLM attempt {attempt + 1}/{max_retry} failed: {e}")
            if attempt < max_retry - 1:
                time.sleep(random.uniform(1, 16))
    return None


# ──────────────────────────────────────────────
# Step 2：Jina 抓取原始内容
# ──────────────────────────────────────────────

def _read_jina(url: str) -> str:
    """抓取网页 Markdown，失败抛异常。"""
    if not JINA_API_KEY:
        raise ValueError("JINA_API_KEY not configured")
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(
            "https://r.jina.ai/",
            headers={
                "Authorization": f"Bearer {JINA_API_KEY}",
                "X-Engine": "direct",
                "Content-Type": "application/json",
                "X-Retain-Images": "none",
                "X-Return-Format": "markdown",
                "X-Timeout": "60",
            },
            json={"url": url},
        )
    resp.raise_for_status()
    return resp.text


# ──────────────────────────────────────────────
# Step 3：LLM 分析（自动分块）
# ──────────────────────────────────────────────

def _get_browse_answer(source_text: str, browse_query: str, max_retry: int = 2) -> str | None:
    """
    用 LLM 按 browse_query 提炼 source_text。
    超过 TOKEN_LIMIT 时自动分块并发处理后合并。
    """
    enc    = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(source_text)

    def _make_prompt(chunk: str) -> str:
        return (
            "Please read the source content and answer a following question:\n"
            "--- begin of source content ---\n"
            f"{chunk}\n"
            "--- end of source content ---\n\n"
            "If there is no relevant information, please clearly refuse to answer.\n"
            "When answering, please identify and extract the original content as the evidence. "
            f"Now answer the question based on the above content:\n{browse_query}"
        )

    if len(tokens) <= TOKEN_LIMIT:
        return _get_response(_make_prompt(source_text), max_retry)

    # 分块并发
    num_split  = math.ceil(len(tokens) / TOKEN_LIMIT)
    chunk_len  = math.ceil(len(tokens) / num_split)
    output     = "Since the content is too long, the result is split and answered separately. Please combine the results to get the complete answer.\n"

    futures = {}
    with ThreadPoolExecutor(max_workers=num_split) as ex:
        for i in range(num_split):
            start = i * chunk_len
            end   = min(start + chunk_len + 1024, len(tokens))
            chunk = enc.decode(tokens[start:end])
            futures[ex.submit(_get_response, _make_prompt(chunk), max_retry)] = i

        outputs = [None] * num_split
        for fut in as_completed(futures):
            outputs[futures[fut]] = fut.result()

    if any(o is None for o in outputs):
        return None

    for i, o in enumerate(outputs):
        output += f"--- begin of result part {i+1} ---\n{o}\n--- end of result part {i+1} ---\n\n"

    return output


# ──────────────────────────────────────────────
# Step 4：单 URL 处理（含 retry + sleep）
# ──────────────────────────────────────────────

def _get_browse_results(url: str, browse_query: str, max_retry: int = MAX_RETRY) -> str:
    """抓取单个 URL 并提炼答案，返回字符串（失败返回错误信息）。"""
    if not url:
        return "URL is missing or empty. Please provide a valid URL."
    if not browse_query:
        browse_query = "Detailed summary of the page."

    time.sleep(random.uniform(0, 16))  # 随机错开并发请求

    source_text = ""
    for attempt in range(max_retry):
        try:
            source_text = _read_jina(url)
            break
        except Exception as e:
            if any(w in str(e).lower() for w in ["client error", "403", "denied"]):
                return "Access to this URL is denied. Please try again."
            logger.warning(f"Jina attempt {attempt + 1}/{max_retry} failed for {url}: {e}")
            if attempt < max_retry - 1:
                time.sleep(random.uniform(1, 16))

    if not source_text.strip():
        return "Browse error. Please try again."

    answer = _get_browse_answer(source_text, browse_query, max_retry=max_retry)
    if not answer or not answer.strip():
        return "Browse error. Please try again."

    return answer.strip()


# ──────────────────────────────────────────────
# 公开接口
# ──────────────────────────────────────────────

def fetch(urls: list[str], browse_query: str = "Detailed summary of the page.") -> str:
    """
    并发抓取多个 URL 并用 LLM 提炼答案。

    Args:
        urls:         URL 列表
        browse_query: 想从页面获取什么

    Returns:
        格式化字符串，每个 URL 对应一块答案
    """
    if not urls:
        return "No URLs provided."
    if not browse_query:
        browse_query = "Detailed summary of the page."

    results = [None] * len(urls)
    with ThreadPoolExecutor(max_workers=len(urls)) as ex:
        futures = {
            ex.submit(_get_browse_results, url, browse_query): i
            for i, url in enumerate(urls)
        }
        for fut in as_completed(futures):
            results[futures[fut]] = fut.result()

    lines = []
    for url, result in zip(urls, results):
        lines.append(f"--- answer based on [{url}] ---\n{result}\n--- end of answer ---")
    return "\n\n".join(lines)


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("用法: python fetch.py <url1> [url2 ...] [browse_query]", file=sys.stderr)
        print("  最后一个参数若不以 http 开头，视为 browse_query", file=sys.stderr)
        sys.exit(1)

    # 最后一个参数若不以 http 开头，视为 browse_query
    if not args[-1].startswith("http"):
        urls, query = args[:-1], args[-1]
    else:
        urls, query = args, "Detailed summary of the page."

    if not urls:
        print("请至少提供一个 URL", file=sys.stderr)
        sys.exit(1)

    print(fetch(urls, query))