# Personal Skills

这是一个个人 Claude Code Skills 仓库，包含自定义的技能扩展。

## 如何添加 Skills 到 Claude Code

### 方法一：直接复制文件

将 skill 文件夹复制到 Claude Code 的 skills 目录：

```bash
# 找到 Claude Code 的 skills 目录
# 通常位于 ~/.claude/skills/ 或项目内的 .claude/skills/

# 复制 skill 文件夹
cp -r skill-name ~/.claude/skills/
```

### 方法二：使用 Git Submodule

```bash
# 在 Claude Code 项目中
git submodule add https://github.com/LakerBlock/Personal-Skills.git .claude/skills/skill-name
git submodule update --init --recursive
```

### 方法三：克隆到指定目录

```bash
# 克隆到 Claude Code skills 目录
cd ~/.claude/skills/
git clone https://github.com/LakerBlock/Personal-Skills.git skill-name
```

## Available Skills

### code-doc-generator

为 Python 项目生成详细的技术说明文档。

**功能**：
- 自顶向下的项目分析
- 时间线驱动的流程追踪
- 详细的输入输出规格
- 代码示例驱动
- 架构图生成（Mermaid）
- 用户偏好记忆

**支持的架构图**：
- 项目目录结构图 (graph TD)
- 模块依赖图 (graph LR)
- 执行流程图 (flowchart TB)
- 数据流图 (flowchart LR)
- 类图 (classDiagram)
- 时序图 (sequenceDiagram)

**使用方法**：

```python
from Skill import code_doc_generator
code_doc_generator.run(project_path="/path/to/your/project")
```

或使用 Skill 工具：

```
使用 Skill 工具调用 code-doc-generator
```

## 添加新的 Skill

1. 在仓库根目录下创建新的 skill 文件夹
2. 添加 `SKILL.md` 文件描述 skill 功能
3. 提交并推送到 GitHub
4. 更新本 README

## License

MIT License
