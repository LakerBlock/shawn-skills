# Personal Skills

A personal Claude Code Skills repository containing custom skill extensions.

## What are Claude Code Skills?

Skills are **self-contained instruction sets** that teach Claude how to perform specific tasks. Each skill is a folder containing:

- `SKILL.md` - Main instruction file with YAML frontmatter
- Supporting files (optional) - Reference guides, examples, scripts

## How to Add Skills to Claude Code

### Method 1: Clone to Skills Directory

```bash
# Find your Claude Code skills directory
# Usually: ~/.claude/skills/ or .claude/skills/

# Clone this repository
cd ~/.claude/skills/
git clone https://github.com/LakerBlock/Personal-Skills.git

# Or clone a specific skill
cd ~/.claude/skills/
git clone https://github.com/LakerBlock/Personal-Skills.git code-doc-generator
```

### Method 2: Copy Skill Folder

```bash
# Copy the skill folder to your skills directory
cp -r /path/to/Personal-Skills/code-doc-generator ~/.claude/skills/
```

### Method 3: Git Submodule (Recommended for Projects)

```bash
# In your Claude Code project directory
git submodule add https://github.com/LakerBlock/Personal-Skills.git .claude/skills/skill-name
git submodule update --init --recursive

# Update all submodules
git submodule update --init --recursive
```

### Method 4: Download Single Skill

```bash
# Download and extract a specific skill
cd ~/.claude/skills/
curl -L https://github.com/LakerBlock/Personal-Skills/archive/refs/heads/main.tar.gz | tar xz
mv Personal-Skills-main code-doc-generator
rm -rf Personal-Skills-main
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md              # Required: Main instructions with YAML frontmatter
├── references/           # Optional: Supporting documentation
│   ├── doc_template.md
│   ├── analysis_patterns.md
│   └── user_preferences.json
├── scripts/              # Optional: Utility scripts
│   └── helper.py
└── assets/               # Optional: Resource files
```

## YAML Frontmatter Format

Every `SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: skill-name
description: A clear description of what this skill does and when to use it. This helps Claude discover and activate the skill appropriately.
---
```

### Frontmatter Requirements

| Field | Requirements |
|-------|-------------|
| `name` | Max 64 chars, lowercase with hyphens, no reserved words |
| `description` | Non-empty, max 1024 chars, describe what and when |

**Reserved words** (cannot use): `anthropic`, `claude`

### Good Description Examples

```yaml
# Good: Specific with use cases
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Good: Third person for system prompt
description: Generates detailed technical documentation for Python projects. Use when users need to understand code flow, initialization process, or detailed code analysis.
```

## Available Skills

### code-doc-generator

Generates detailed technical documentation for Python projects.

**Features**:
- Top-down project analysis
- Timeline-driven execution tracing
- Detailed input/output specifications
- Code example driven
- Mermaid architecture diagrams
- User preference memory

**Architecture Diagrams**:
- Project directory structure (graph TD)
- Module dependency graph (graph LR)
- Execution flow diagram (flowchart TB)
- Data flow diagram (flowwatch LR)
- Class diagram (classDiagram)
- Sequence diagram (sequenceDiagram)

**Usage**:

Use the Skill tool:
```
Use Skill tool to invoke code-doc-generator
```

Or call directly:
```python
from Skill import code_doc_generator
code_doc_generator.run(project_path="/path/to/your/project")
```

## Skill Naming Conventions

Recommended: **Gerund form** (verb + -ing):
- `processing-pdfs`
- `analyzing-code`
- `writing-documentation`

Acceptable alternatives:
- `pdf-processing`
- `code-analysis`

**Avoid**:
- Vague names: `helper`, `utils`
- Overly generic: `documents`, `data`
- Reserved words: `anthropic-helper`, `claude-tools`

## Best Practices

Based on Anthropic's official guidelines:

### Writing Effective SKILL.md

1. **Keep it concise** - Challenge each piece of information
2. **Use third person** - For system prompt injection
3. **Be specific** - Include key terms for discoverability
4. **Progressive disclosure** - Keep main file under 500 lines
5. **Use references** - Link to detailed files

### Architecture Diagrams

Follow the patterns in `SKILL.md`:
- Every project needs directory structure + execution flow
- Complex projects add module dependency + data flow
- Multi-class projects add class + sequence diagrams

## Adding New Skills

1. Create a new folder under skill name
2. Add `SKILL.md` with proper YAML frontmatter
3. Include supporting files if needed
4. Update this README
5. Commit and push to GitHub

### Skill Template

```yaml
---
name: new-skill-name
description: A clear description of what this skill does and when to use it.
---

# New Skill Name

[Add your instructions here]

## Use Cases
- Example 1
- Example 2

## Guidelines
- Guideline 1
- Guideline 2
```

## References

- [Official Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Claude Code Documentation](https://code.claude.com/docs/en/skills)

## License

MIT License
