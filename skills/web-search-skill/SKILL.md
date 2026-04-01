---
name: web-search-skill
description: >
  使用 Serper（Google 搜索）和 Jina + LLM（网页内容理解）执行联网搜索。
  当用户需要搜索网页或理解 URL 内容时触发此 skill。
---

# Web Search Skill

## 调用方式

统一通过 `run.sh` 调用，**使用绝对路径，无需手动 cd 或激活 venv**。
首次运行时自动安装依赖，之后直接执行。

```bash
# $SKILL_PATH = skill 目录绝对路径，例如：
# /Users/shawn/.claude/plugins/marketplaces/shawn-skills/skills/web-search-skill

bash $SKILL_PATH/run.sh search "Claude AI" "LLM inference"
bash $SKILL_PATH/run.sh fetch https://example.com "核心观点是什么？"
bash $SKILL_PATH/run.sh fetch https://bbc.com https://cnn.com "今日头条"
```

---

## 脚本接口

### `run.sh search` — 批量 Google 搜索

**输入：** 一个或多个搜索词，支持 Google 高级语法（`site:`、`intitle:` 等）

**输出（str）：**
```
--- search result for [Claude AI] ---
<title>...</title>
<url>https://...</url>
<snippet>...</snippet>
--- end of search result ---
```

---

### `run.sh fetch` — 多 URL 并发抓取 + LLM 理解

内部流程：`Jina 抓取原始 Markdown` → `BROWSE_MODEL 按 browse_query 提炼答案`
超过 120k tokens 时自动分块并发处理后合并，多 URL 并发执行。

**输入：** 一个或多个 URL，最后一个非 `http` 开头的参数视为 `browse_query`

**输出（str）：**
```
--- answer based on [https://example.com] ---
LLM 提炼后的答案...
--- end of answer ---
```

---

## 错误输出

错误信息直接嵌入输出字符串：

| 场景 | 输出内容 |
|------|---------|
| API Key 未设置 | `Error: SERPER_API_KEY not configured.` |
| Jina 被拒（403）| `Access to this URL is denied. Please try again.` |
| 抓取/LLM 失败 | `Browse error. Please try again.` |
| 搜索结果为空 | `Search result is empty. Please try with more general and valid queries.` |