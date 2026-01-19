# Shawn Skills

Personal Claude Code Skills collection.

## Installation

### Method 1: Claude Code Plugin Marketplace (Recommended)

```bash
# Add marketplace
claude plugin marketplace add LakerBlock/shawn-skills

# Install skills
claude plugin install code-doc-generator@shawn-skills
claude plugin install algorithm-explanator@shawn-skills
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

## License

MIT
