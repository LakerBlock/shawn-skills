---
name: web-search-skill
description: >
  使用 Serper（Google 搜索）和 Jina + LLM（网页内容理解）执行联网搜索。
  当用户需要搜索网页或理解 URL 内容时触发此 skill。
---

# Web Search Skill

## 环境安装

首次使用前，在 skill 目录下执行一次：

```bash
bash setup.sh
```

这会创建 `.venv` 并安装 `httpx`、`tiktoken`、`openai`。

之后每次调用脚本前激活环境：

```bash
source .venv/bin/activate
```

---

## 脚本接口

### `scripts/search.py` — 批量 Google 搜索

**调用方式：**
```bash
python scripts/search.py "Claude AI" "LLM inference"
```
```python
from scripts.search import search
result = search(["Claude AI", "LLM inference"])
```

**输入：** `queries: list[str]`，支持 Google 高级语法（`site:`、`intitle:` 等）

**输出（str）：**
```
--- search result for [Claude AI] ---
<title>...</title>
<url>https://...</url>
<snippet>...</snippet>
--- end of search result ---
```

---

### `scripts/fetch.py` — 多 URL 并发抓取 + LLM 理解

内部流程：`Jina 抓取原始 Markdown` → `BROWSE_MODEL 按 browse_query 提炼答案`
超过 120k tokens 时自动分块并发处理后合并。多 URL 并发执行。

**调用方式：**
```bash
# 单个 URL（默认全文摘要）
python scripts/fetch.py https://example.com

# 单个 URL + 指定问题（最后一个非 http 参数视为 browse_query）
python scripts/fetch.py https://example.com "核心观点是什么？"

# 多个 URL + 同一问题
python scripts/fetch.py https://bbc.com https://cnn.com "今日头条"
```
```python
from scripts.fetch import fetch
result = fetch(["https://bbc.com", "https://cnn.com"], browse_query="今日头条")
```

**输入：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `urls` | `list[str]` | URL 列表，多个并发处理 |
| `browse_query` | `str`（可选）| 想从页面获取什么，默认全文摘要 |

**输出（str）：**
```
--- answer based on [https://bbc.com] ---
LLM 提炼后的答案...
--- end of answer ---

--- answer based on [https://cnn.com] ---
LLM 提炼后的答案...
--- end of answer ---
```

---

## 错误输出

两个脚本均直接在输出字符串中内嵌错误信息（与 MCP server 行为一致）：

| 场景 | 输出内容 |
|------|---------|
| API Key 未设置 | `Error: SERPER_API_KEY not configured.` |
| Jina 被拒（403）| `Access to this URL is denied. Please try again.` |
| 抓取/LLM 失败 | `Browse error. Please try again.` |
| 搜索结果为空 | `Search result is empty. Please try with more general and valid queries.` |