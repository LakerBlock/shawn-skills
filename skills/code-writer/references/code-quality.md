# 代码质量标准参考

> 由 `SKILL.md` Phase 1 引用。做代码质量决策时读此文件。

---

## 1. 函数设计

### 单一职责
```python
# ✅ 一个函数做一件事
def parse_date(raw: str) -> datetime:
    ...

def validate_order(order: dict) -> None:
    ...

def process_order(order: dict) -> Receipt:
    validate_order(order)
    ...

# ❌ 一个函数做三件事
def process(raw_str):
    date = datetime.strptime(raw_str, "%Y-%m-%d")  # 解析
    if date < datetime.now():                        # 验证
        raise ValueError(...)
    return {"date": date, "status": "ok"}           # 转换
```

### 函数长度
- **< 20 行**：理想，一屏可读
- **20–40 行**：可接受，考虑是否可以拆
- **> 40 行**：必须拆分，无例外

---

## 2. 命名规范（Python）

```python
# 变量/函数/方法：snake_case
user_count = 0
def calculate_rmse(y_true, y_pred): ...

# 类：PascalCase
class DataLoader: ...
class LinearRegression: ...

# 常量：UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECS = 30.0

# Private：单下划线前缀
self._cache = {}
def _parse_internal(self): ...

# 避免：
x, tmp, data2, flag, result  # 无语义名
AbstractBaseManagerFactory    # 过度工程
```

---

## 3. 类型注解

所有 public 函数必须加完整类型注解：

```python
from __future__ import annotations
from typing import Sequence

# ✅ 完整注解
def clip(
    values: Sequence[float],
    low: float = 0.0,
    high: float | None = None,
) -> list[float]:
    ...

# ✅ 类方法
class Model:
    def fit(self, X: Sequence[float], y: Sequence[float]) -> "Model":
        ...

    def predict(self, X: Sequence[float]) -> list[float]:
        ...

# ❌ 没有注解
def clip(values, low=0.0, high=None):
    ...
```

---

## 4. Docstring 规范

Public API 必须有 docstring，格式统一用 Google style：

```python
def mae(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """Compute Mean Absolute Error.

    Args:
        y_true: Ground-truth target values.
        y_pred: Predicted values. Must have the same length as y_true.

    Returns:
        Scalar MAE value.

    Raises:
        ValueError: If inputs have different lengths or are empty.

    Example:
        >>> mae([1.0, 2.0], [1.5, 2.5])
        0.5
    """
```

**最低要求**：一行摘要 + Raises（如果有异常路径）。

---

## 5. 错误处理

```python
# ✅ 具体的 exception 类型 + 有意义的消息
def fit(self, X, y):
    if len(X) != len(y):
        raise ValueError(
            f"X and y must have the same length, "
            f"got {len(X)} and {len(y)}"
        )
    if len(X) < 2:
        raise ValueError(f"Need at least 2 samples, got {len(X)}")

# ❌ 裸 Exception + 无信息消息
def fit(self, X, y):
    if len(X) != len(y):
        raise Exception("error")

# ❌ 静默吞异常
try:
    result = parse(raw)
except Exception:
    result = None   # 调用方永远不知道出了什么问题
```

---

## 6. 避免的反模式

| 反模式 | 问题 | 替代 |
|--------|------|------|
| `except Exception: pass` | 隐藏错误 | 至少 log，最好 re-raise |
| 嵌套三层以上的 if | 可读性差 | early return / guard clause |
| 函数参数 > 5 个 | 难以调用/测试 | 用 dataclass 或 TypedDict 封装 |
| 可变默认参数 `def f(x=[])` | Python 陷阱 | `def f(x=None): x = x or []` |
| 全局可变状态 | 难以测试 | 通过参数传入，或用类封装 |
| 魔法数字 `if status == 3` | 不可读 | `if status == OrderStatus.CANCELLED` |

---

## 7. 导入规范

```python
# 顺序：标准库 → 第三方 → 本地包，组间空行
import math
import os
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from src.utils.metrics import mae, rmse
from src.models.linear import LinearRegression

# ✅ 明确导入，避免 *
from src.utils import mae, rmse

# ❌ 避免
from src.utils import *
```

---

## 8. 注释原则

```python
# ✅ 注释说"为什么"，而不是"是什么"
# clip from below at 0: predictions can't be negative orders
preds = [max(0.0, p) for p in raw_preds]

# ❌ 说废话的注释（代码已经很清楚了）
# add 1 to i
i += 1

# ✅ TODO 注释要带上具体说明
# TODO(shawn): replace with vectorized numpy op when dataset > 1M rows
result = [process(x) for x in data]
```