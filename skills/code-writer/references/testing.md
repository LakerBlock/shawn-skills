# 测试工程参考手册

> 由 `SKILL.md` 中 Phase 2 引用。遇到测试设计决策时读此文件。

---

## 1. 目录结构规范

```
project/
├── src/
│   ├── __init__.py
│   ├── module_a.py
│   └── sub_pkg/
│       ├── __init__.py
│       └── module_b.py
└── test/                        ← 与 src/ 平行
    ├── conftest.py              ← 全局 fixtures
    ├── test_module_a.py
    └── sub_pkg/
        ├── conftest.py          ← 子包专属 fixtures（按需）
        └── test_module_b.py
```

**强制规则**：每个 `src/a/b.py` 对应 `test/a/test_b.py`，一一映射。

---

## 2. 命名约定

| 对象 | 规范 | 示例 |
|------|------|------|
| 测试文件 | `test_<module>.py` | `test_metrics.py` |
| 测试函数 | `test_<what>_<condition>_<expected>` | `test_mae_empty_input_raises` |
| 测试类 | `class Test<Feature>:` | `class TestLinearRegression:` |
| Fixture | 名词，描述返回值 | `sample_df`, `fitted_model` |

---

## 3. pyproject.toml 最小配置

```toml
[tool.pytest.ini_options]
minversion  = "7.0"
addopts     = "-ra -q --tb=short"
testpaths   = ["test"]
pythonpath  = ["src"]          # src layout 必须加

[tool.pytest.ini_options.markers]
unit        = "fast, no I/O"
integration = "requires external resources"
slow        = "takes > 1s"
```

---

## 4. 测试设计决策树

```
需要测什么？
│
├─ Public 函数 / 方法
│   ├─ 正常输入（happy path）         → 必测
│   ├─ 边界值（空、None、0、最大值）   → 必测
│   └─ 异常路径（错误类型/消息）       → 必测
│
├─ 类的状态机
│   ├─ 初始状态                       → 必测
│   ├─ 操作后状态变化                  → 必测
│   └─ 非法操作顺序（如未 fit 就 predict）→ 必测
│
├─ Private 方法（_开头）
│   └─ 通过 public 接口间接覆盖        → 不直接测
│
└─ 第三方库行为
    └─ 不测                            → 信任第三方
```

---

## 5. 模板：标准测试文件

```python
"""
Tests for src/<module_path>.py

Covers:
  - <FeatureA>: happy path, edge cases, errors
  - <FeatureB>: state transitions
"""
import pytest
from <module_path> import <TargetClass>, <target_func>


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_input():
    """Minimal valid input shared across tests in this file."""
    return {"key": "value"}


# ── Happy Path ────────────────────────────────────────────────────────────────

class TestTargetFunc:
    def test_returns_expected_on_valid_input(self, sample_input):
        result = target_func(sample_input)
        assert result == expected_value

    def test_handles_empty_container(self):
        assert target_func([]) == default_value

    @pytest.mark.parametrize("inp,expected", [
        (case_a_input, case_a_expected),
        (case_b_input, case_b_expected),
    ])
    def test_parametrized_cases(self, inp, expected):
        assert target_func(inp) == pytest.approx(expected)


# ── Error Handling ────────────────────────────────────────────────────────────

    @pytest.mark.parametrize("bad_input,exc_type,match", [
        (None,  TypeError,  ""),
        (-1,    ValueError, "must be positive"),
    ])
    def test_raises_on_invalid_input(self, bad_input, exc_type, match):
        with pytest.raises(exc_type, match=match):
            target_func(bad_input)


# ── Class State ───────────────────────────────────────────────────────────────

class TestTargetClass:
    def test_initial_state(self):
        obj = TargetClass()
        assert obj.is_ready is False

    def test_state_after_setup(self):
        obj = TargetClass()
        obj.setup()
        assert obj.is_ready is True

    def test_operation_before_setup_raises(self):
        with pytest.raises(RuntimeError, match="not ready"):
            TargetClass().operate()
```

---

## 6. conftest.py 模板

```python
# test/conftest.py
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def tmp_dir(tmp_path):
    """Fresh temp directory per test — never shared."""
    return tmp_path


@pytest.fixture
def sample_records():
    return [
        {"id": 1, "value": 10.0},
        {"id": 2, "value": 20.0},
    ]
```

**Fixture scope 选择**：

| scope | 适用场景 |
|-------|---------|
| `function`（默认） | 任何含可变状态的对象，数据库连接 |
| `class` | 同一 class 内所有测试共享的只读数据 |
| `module` | 整个文件共享的重型只读资源（解析大文件） |
| `session` | 整次测试运行不变的常量（路径、配置） |

---

## 7. Mock 使用原则

```python
from unittest.mock import patch, MagicMock

# ✅ 正确：mock 外部依赖
def test_fetch_calls_api(mocker):
    mock_get = mocker.patch("src.client.requests.get")
    mock_get.return_value.json.return_value = {"data": []}
    result = fetch_data("http://api.example.com")
    mock_get.assert_called_once_with("http://api.example.com", timeout=30)
    assert result == []

# ✅ 正确：mock 时间，避免测试抖动
def test_rate_limiter(mocker):
    mock_time = mocker.patch("src.limiter.time.monotonic")
    mock_time.return_value = 1000.0
    ...

# ❌ 错误：mock 了被测函数自身，什么都没测
def test_wrong(mocker):
    mocker.patch("src.module.target_func", return_value=42)
    assert target_func() == 42
```

**Mock 决策规则**：

- 外部 HTTP/gRPC 调用 → 必须 mock
- 文件 IO（读/写真实文件）→ 用 `tmp_path` fixture，不 mock
- 数据库 → 用内存 DB 或 mock，视复杂度决定
- `time.time()` / `datetime.now()` → mock，保证确定性
- 被测模块内部的私有函数 → **不 mock**，通过 public 接口测

---

## 8. 回归保护脚本（完整版）

```bash
# 使用方式：
# 步骤1 - 捕获基线（改动前）
python -m pytest test/ -q --tb=no 2>&1 | tee /tmp/baseline.txt

# 步骤2 - 做改动，写测试

# 步骤3 - 运行全量测试
python -m pytest test/ -v --tb=short 2>&1 | tee /tmp/after.txt

# 步骤4 - 对比
python3 - <<'EOF'
import re

def parse(path):
    try:
        content = open(path).read()
    except FileNotFoundError:
        return set(), set()
    return (
        set(re.findall(r"PASSED\s+(\S+)", content)),
        set(re.findall(r"FAILED\s+(\S+)", content)),
    )

base_pass, base_fail = parse("/tmp/baseline.txt")
curr_pass, curr_fail = parse("/tmp/after.txt")

regressions = base_pass & curr_fail

if regressions:
    print("❌  REGRESSION:")
    for t in sorted(regressions):
        print(f"    {t}")
else:
    new_passes = curr_pass - base_pass
    print(f"✅  Clean. +{len(new_passes)} new passing tests | "
          f"total passing: {len(curr_pass)}")
EOF
```

---

## 9. 测试覆盖率参考基准

| 代码类型 | 推荐覆盖目标 | 说明 |
|---------|------------|------|
| 核心算法 / 数据处理 | ≥ 90% | 每条分支都应有对应测试 |
| API 接口层 | ≥ 80% | 重点覆盖正常路径和错误路径 |
| 胶水代码 / 配置 | ≥ 60% | 避免为凑覆盖率写无意义测试 |
| UI 渲染 / 可视化 | 视情况 | 优先集成测试而非单元测试 |

> 覆盖率是信号，不是目标。一个覆盖率 95% 但全是 `assert result is not None` 的套件毫无价值。

---

## 10. 常见报错速查

### ImportError / ModuleNotFoundError
```bash
# 确认 src 在 Python 路径中
export PYTHONPATH=src:$PYTHONPATH
# 或在 pyproject.toml 加：pythonpath = ["src"]
```

### 测试间状态污染（某些测试单独跑通，一起跑就失败）
```python
# 使用 function scope（默认），不要对可变对象用 session scope
@pytest.fixture          # scope 默认是 "function"
def fresh_state():
    state = MyState()
    yield state
    state.reset()        # teardown — 无论 pass/fail 都会执行
```

### 参数化测试 ID 不可读
```python
# 加 id= 让失败信息更直观
@pytest.mark.parametrize("x,expected", [
    pytest.param(0,   0.0, id="zero"),
    pytest.param(-1, -1.0, id="negative"),
    pytest.param(100, 100.0, id="large"),
])
```

### `pytest.approx` 的使用时机
```python
# 浮点比较必须用 approx
assert result == pytest.approx(3.14159, abs=1e-4)  # 绝对误差
assert result == pytest.approx(1.0, rel=1e-6)       # 相对误差

# 列表/字典也支持
assert [0.1 + 0.2, 0.3] == pytest.approx([0.3, 0.3])
```