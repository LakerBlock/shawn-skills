# Shawn Skills

Personal Claude Code Skills collection.

## Installation

### Method 1: Claude Code Plugin Marketplace (Recommended)

```bash
# Add marketplace
claude plugin marketplace add LakerBlock/shawn-skills

# Install plugin
claude plugin install shawn-skills
```

### Method 2: Manual Installation

```bash
# Clone to skills directory
git clone https://github.com/LakerBlock/shawn-skills.git ~/.claude/skills/shawn-skills
```

## Available Skills

### code-doc-generator

为 Python 项目生成详细的技术文档。

**使用场景**:
- "帮我写一个文档介绍这个项目的训练流程"
- "分析一下模型初始化时每个时间点做了什么"
- "生成一份数据流文档"
- "这个模块是怎么工作的？"

### code-writer

通用代码工程 Skill。写代码、改代码、加功能、重构、调试、写测试、补测试、修 bug，只要涉及动代码，就触发此 skill。

**核心承诺**：
- 所有改动必须经过测试验证
- 测试写在 `/test` 目录下的对应子模块
- 绝不让已通过的测试变成失败（no pass-to-fail）

**使用场景**:
- "帮我实现这个功能"
- "重构这段代码"
- "修这个 bug"
- "给这个模块补测试"
- "优化这段代码的性能"

### algorithm-explanator

通用算法解释框架。用直观的比喻、逐步图解、代码对照的方式解释任何算法问题的核心思路、变量设计逻辑、循环结构设计的思考过程。

**使用场景**:
- "解释这道股票交易算法题"
- "帮我理解动态规划的状态设计"
- "这个算法为什么要这样定义变量？"
- "讲解一下这段代码的循环结构"
- "如何在面试中条理清晰地解释算法题？"

**核心特点**:
- 小学生也能看懂的比喻（两个口袋的故事）
- 每段代码都有详细解释
- 深入解释"为什么这样设计"的逻辑思考过程
- 包含面试答题模板（5分钟版）

### chrome-cdp

Chrome DevTools Protocol CLI。直接通过 WebSocket 连接本地 Chrome，无需 Puppeteer，支持 100+ 标签页，即时连接。

**使用场景**:
- "帮我截图当前打开的页面"
- "获取这个页面的可访问性树"
- "在 Chrome 里执行这段 JS"
- "点击查看这个元素"

**前置条件**:
- Chrome 已开启远程调试（打开 `chrome://inspect/#remote-debugging` 并开启开关）
- Node.js 22+

## License

MIT
