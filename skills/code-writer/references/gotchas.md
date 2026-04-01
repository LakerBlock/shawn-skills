# Gotchas：高频踩坑记录

> 由 `SKILL.md` 在遇到奇怪行为时引用。
> 这里收录的是 AI 辅助编码中最容易出现、且最难自查的问题。

---

## G1. Import 类错误

### `ModuleNotFoundError: No module named 'src'`
```bash
# 症状：pytest 找不到 src/ 下的模块
# 原因：src/ 不在 Python 路径中

# 修复1：pyproject.toml 加 pythonpath
[tool.pytest.ini_options]
pythonpath = ["src"]

# 修复2：环境变量
export PYTHONPATH=src:$PYTHONPATH

# 修复3：src/ 下加 __init__.py
touch src/__init__.py
```

### `ImportError: cannot import name 'X' from 'Y'`
```bash
# 先确认函数名没有拼写错误
grep -n "def X" src/module.py

# 确认 __init__.py 是否显式 re-export
cat src/__init__.py
```

---

## G2. 测试隔离问题

### 单独跑通，一起跑就失败（测试顺序依赖）
```python
# 原因：某个测试修改了全局状态，影响了后续测试

# 诊断
pytest test/ -v --randomly-seed=0   # 固定顺序
pytest test/ -v -p no:randomly       # 禁止随机顺序
pytest test/test_a.py test/test_b.py -v  # 手动指定顺序复现

# 修复：用 fixture teardown 清理状态
@pytest.fixture
def app_state():
    state = AppState()
    yield state
    state.reset()   # ← 无论 pass/fail 都执行
```

### Fixture `scope="session"` 意外共享可变对象
```python
# ❌ 危险：session scope 的列表被修改后影响所有测试
@pytest.fixture(scope="session")
def records():
    return [{"id": 1}]   # 如果某个测试 records.append(...)，影响后续

# ✅ 安全：function scope（默认）保证每次新建
@pytest.fixture
def records():
    return [{"id": 1}]
```

---

## G3. 浮点精度问题

```python
# ❌ 直接比较浮点数
assert 0.1 + 0.2 == 0.3          # 失败！

# ✅ 使用 pytest.approx
assert 0.1 + 0.2 == pytest.approx(0.3)
assert result == pytest.approx(expected, abs=1e-6)   # 绝对误差
assert result == pytest.approx(expected, rel=1e-4)   # 相对误差

# ✅ 列表和字典也支持
assert predictions == pytest.approx([1.0, 2.0, 3.0], abs=0.01)
```

---

## G4. Mock 失效

### `patch` 路径写错（最常见的 Mock 错误）
```python
# src/client.py 里：import requests; requests.get(...)
# ❌ 错误：patch 的是原始位置，但 client.py 已经 import 进来了
mocker.patch("requests.get")

# ✅ 正确：patch 的是被测模块看到的名字
mocker.patch("src.client.requests.get")

# 规则：patch WHERE IT IS USED，不是 where it is defined
```

### Mock 在测试结束后没有还原
```python
# 用 mocker（pytest-mock）自动还原，不用手动 mock.patch.stopall()
def test_something(mocker):
    mocker.patch("src.module.func")
    # 测试结束后 mocker 自动还原，无需手动 stop
```

---

## G5. 参数化测试的常见错误

```python
# ❌ 参数名和函数参数不匹配
@pytest.mark.parametrize("input,expected", [...])
def test_something(inp, expected):   # 应该是 "input" 不是 "inp"
    ...

# ❌ 只有一个参数时忘记去掉元组
@pytest.mark.parametrize("x", [(1,), (2,)])  # 传入的是元组，不是整数
def test_something(x):
    assert x == 1    # x 实际是 (1,)，失败

# ✅ 正确
@pytest.mark.parametrize("x", [1, 2])
def test_something(x):
    assert isinstance(x, int)
```

---

## G6. 文件/路径相关测试

```python
# ❌ 使用硬编码路径，在不同机器上失败
def test_load_file():
    df = load("/home/user/project/data/sample.csv")

# ✅ 使用 tmp_path fixture 创建临时文件
def test_load_file(tmp_path):
    sample = tmp_path / "sample.csv"
    sample.write_text("id,value\n1,10\n2,20\n")
    df = load(str(sample))
    assert len(df) == 2

# ✅ 使用 pathlib + __file__ 引用测试数据
FIXTURES_DIR = Path(__file__).parent / "fixtures"
def test_load_fixture():
    df = load(str(FIXTURES_DIR / "sample.csv"))
```

---

## G7. 异常测试的细节

```python
# ❌ 只捕获类型，不验证消息（太宽松）
with pytest.raises(ValueError):
    target_func(bad_input)

# ✅ 同时验证消息（match 是正则表达式）
with pytest.raises(ValueError, match="must be positive"):
    target_func(-1)

with pytest.raises(ValueError, match=r"length \d+ != \d+"):
    target_func(mismatched_inputs)

# ⚠️ 注意：pytest.raises 只捕获 with 块内的第一个异常
# 测试函数的 setup 抛的异常不会被捕获
with pytest.raises(ValueError):
    setup_that_might_also_raise()   # ← 这里的异常不会被捕获为"预期"
    target_func(bad_input)          # ← 这里的异常才是目标
```

---

## G8. 回归脚本解析失败

```bash
# 症状：回归脚本输出 "New passes: 0 | Total: 0"（明显不对）
# 原因：baseline.txt 格式与正则不匹配

# 调试：手动检查格式
cat /tmp/baseline.txt | grep -E "PASSED|FAILED" | head -5

# pytest -v 输出格式：
# test/utils/test_metrics.py::TestMae::test_basic PASSED
# 正则 r"PASSED\s+(\S+)" 从右侧匹配，注意顺序是 "PASSED  test_id"

# 如果使用 pytest -q（quiet mode），格式不同，切换到 -v
python -m pytest test/ -v --tb=no 2>&1 | tee /tmp/baseline.txt
```

---

## G9. 与 AI 辅助编码特有的坑

### AI 生成的测试通过了但什么都没测试
```python
# AI 容易生成这种"通过但无效"的测试
def test_model_works():
    model = LinearRegression()
    result = model.fit([1, 2, 3], [2, 4, 6])
    assert result is not None    # ← 只要不报错就通过，没有验证正确性

# ✅ 要求验证具体值
def test_model_recovers_correct_coef():
    model = LinearRegression().fit([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
    assert model.coef_ == pytest.approx(2.0)
    assert model.intercept_ == pytest.approx(0.0)
```

### AI 删除了失败的测试而不是修复代码
```
症状：回归脚本显示 ✅，但测试数量比基线少了
诊断：git diff test/ | grep "^-def test_"
规则：测试数量只能增加，不能减少（除非有明确理由）
```

### AI 改了测试来通过新代码（而不是改代码）
```
症状：测试改变了预期值，原来期望 X 现在期望 Y
诊断：git diff test/ | grep "^-.*assert\|^+.*assert"
规则：只有 spec 变了才能改测试的预期值，否则应该修复实现
```