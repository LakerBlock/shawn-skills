---
name: code-writer
description: >
  通用代码工程 Skill。写代码、改代码、加功能、重构、调试、写测试、补测试、修 bug，
  只要涉及动代码，就触发此 skill。
  触发关键词：写代码、实现、重构、加功能、修 bug、优化、implement、refactor、
  add feature、fix、代码质量、测试、test、regression、代码评审。
  核心承诺：所有改动必须经过测试验证，测试写在 /test 目录下的对应子模块，
  绝不让已通过的测试变成失败（no pass-to-fail）。
---

# Code Writer Skill

## 总览：编码的四个阶段

每次代码任务，无论大小，都经过同一个循环：

```
理解  →  实现  →  测试  →  收尾
```

**测试不是可选项**。实现和测试是同一个任务的两半。

---

## Phase 0：理解（先读后写）

```bash
# 1. 看项目结构
find . -type f -name "*.py" | sort | head -40
ls -R src/ test/ 2>/dev/null

# 2. 读被改动模块的当前接口
cat src/<target_module>.py

# 3. 捕获测试基线（绝对不跳过）
python -m pytest test/ -q --tb=no 2>&1 | tee /tmp/baseline.txt
cat /tmp/baseline.txt | tail -3
```

**基线原则**：只有知道哪些测试现在是绿的，才能保证改动后不破坏它们。
若项目尚无测试，基线为空，记录下来，继续。

---

## Phase 1：实现

### 1.1 写代码前先明确约束

在动手之前，在脑子里对齐这几点：

| 约束 | 要问的问题 |
|------|-----------|
| **接口** | 改动是否影响已有的公开函数签名？ |
| **兼容性** | 本 skill 只考虑最新接口，不做向后兼容 |
| **副作用** | 有没有文件 IO、网络、全局状态需要隔离？ |
| **最小改动** | 有没有比我想的更简单的实现？ |

### 1.2 代码质量标准

写代码时遵循以下原则（深度参考 → `references/code-quality.md`）：

- **可读性优先**：命名清晰，一个函数只做一件事
- **错误处理显式**：不静默吞异常，用具体的 exception 类型
- **类型注解**：所有 public 函数加 type hints
- **文档字符串**：public API 必须有 docstring（一行摘要 + 参数说明）
- **避免魔法数字**：用命名常量或枚举替代裸字面量

```python
# ✅ 好的示范
def clip_predictions(values: list[float], low: float = 0.0) -> list[float]:
    """Clip values to be no less than `low`.

    Args:
        values: Raw model predictions.
        low: Minimum allowed value (default 0.0).

    Returns:
        List of clipped values.
    """
    return [max(low, v) for v in values]

# ❌ 避免
def cp(v, l=0):
    return [max(l, x) for x in v]
```

### 1.3 实现节奏

```
写一个功能点 → 立即可以被测试 → 不攒大批改动
```

大需求拆成独立可测的小单元，每个单元完成后就运行一次测试。

---

## Phase 2：测试（核心）

> **完整测试规范见 → `references/testing.md`**
> 遇到任何测试相关决策时都应先读该文件。

### 2.1 测试与源码的对应关系

```
src/
├── module_a.py            →  test/test_module_a.py
├── models/
│   └── linear.py          →  test/models/test_linear.py
└── utils/
    └── metrics.py         →  test/utils/test_metrics.py
```

每个源码子模块在 `test/` 下都有对应的测试文件，目录结构完全镜像。

### 2.2 写测试的最低要求

每次新增或修改代码，**必须**同步完成：

1. 为新增的 public 函数写至少一个 happy path 测试
2. 为每个异常分支写对应的 `pytest.raises` 测试
3. 为已知 bug 的修复写一个回归测试（防止复现）

详细的测试设计模式见 `references/testing.md`。

### 2.3 运行测试的节奏

```bash
# 开发中：只跑当前模块的测试，快速反馈
python -m pytest test/path/to/test_target.py -v

# 完成实现后：全量回归
python -m pytest test/ -v --tb=short 2>&1 | tee /tmp/after.txt
```

### 2.4 回归保护（必须执行）

```bash
python3 - <<'EOF'
import re

def parse(path):
    try:
        content = open(path).read()
    except FileNotFoundError:
        return set(), set()
    passed = set(re.findall(r"PASSED\s+(\S+)", content))
    failed = set(re.findall(r"FAILED\s+(\S+)", content))
    return passed, failed

base_pass, base_fail = parse("/tmp/baseline.txt")
curr_pass, curr_fail = parse("/tmp/after.txt")

regressions = base_pass & curr_fail
new_failures = curr_fail - base_fail

if regressions:
    print("❌  REGRESSION — previously passing tests now fail:")
    for t in sorted(regressions): print(f"    {t}")
    print("\n→ 必须修复这些回归才能继续。")
elif new_failures:
    print("⚠️  NEW FAILURES (were already failing at baseline):")
    for t in sorted(new_failures): print(f"    {t}")
else:
    new_passes = curr_pass - base_pass
    print(f"✅  No regressions. +{len(new_passes)} new passing tests.")
EOF
```

**如果输出 ❌，必须修复回归，不得跳过。**

---

## Phase 3：收尾

### 3.1 完成检查清单

```
[ ] 所有新增 public 函数有 type hints + docstring
[ ] 没有注释掉的死代码残留
[ ] 没有 print/logging.debug 调试残留
[ ] 测试覆盖了 happy path + 异常路径
[ ] 全量 pytest 通过，回归脚本输出 ✅
[ ] 改动逻辑清晰，如果需要，更新相关注释
```

### 3.2 提交信息规范

```
<type>(<scope>): <简短描述>

[可选正文：解释为什么，而不是是什么]
[Tests: 新增/修改了哪些测试]
```

类型前缀：`feat` / `fix` / `refactor` / `test` / `docs` / `chore`

示例：
```
feat(metrics): add clip() function with optional upper bound

Previously predictions could go negative.  clip() enforces a floor
(and optional ceiling) as a post-processing step.

Tests: test/utils/test_metrics.py::TestClip (8 cases)
```

---

## Gotchas（高频失误清单）

> 这里记录的是最容易踩的坑，优先于所有其他规则。

| # | 坑 | 正确做法 |
|---|-----|---------|
| 1 | **跳过基线捕获**，直接写代码 | 永远先跑 `pytest --tb=no` 捕获基线 |
| 2 | **测试文件放错位置**（不镜像源码结构） | `src/a/b.py` → `test/a/test_b.py` |
| 3 | **测试 private 方法**（`_开头`） | 通过 public 接口间接测试 |
| 4 | **Mock 了被测函数本身** | 只 mock 外部依赖（IO/网络/时间） |
| 5 | **`assert result is not None`** 这类无意义断言 | 断言具体值/类型/状态 |
| 6 | **回归脚本输出 ❌ 却继续提交** | 必须先修复回归 |
| 7 | **新增功能不写测试** | 测试是实现的一部分，不是额外工作 |
| 8 | **大段改动攒在一起测** | 小步骤，每个功能点立即验证 |

---

## 参考文件索引

| 文件 | 加载时机 |
|------|---------|
| `references/testing.md` | 设计测试、选测试类型、写 fixture、Mock 决策时 |
| `references/code-quality.md` | 做代码质量决策、命名、错误处理、类型注解时 |
| `references/gotchas.md` | 遇到奇怪行为、import 报错、测试不稳定时 |