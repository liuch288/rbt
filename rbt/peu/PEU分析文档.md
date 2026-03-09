# PEU 模块分析文档

## 1. 概述

**PEU** (PnL Estimation Unit) 是 RBT 量化回测框架中的核心组件之一，负责**评估交易策略的潜在损益**。

在 RBT 架构中：
- **DMU** (Decision Making Unit) - 分析市场数据，生成交易信号
- **PEU** (PnL Estimation Unit) - 评估给定信号的潜在收益

PEU 接收 DMU 产生的信号，结合历史市场数据，模拟订单执行过程，最终输出预估损益（pnl）和交易完成时间（finish_time）。

---

## 2. 架构设计

### 2.1 基类定义

所有 PEU 继承自 `PnlEstimateUnit`，它继承自 `Unit` 基类：

```
Unit (unit.py)
    ↓
PnlEstimateUnit (pnl_estimate_unit.py)
    ↓
    ├── BtsSimplePEU
    ├── SimpleBiquotePEU
    ├── BiquotePEU
    ├── BiquoteClosePEU
    └── BiquoteStopClosePEU
```

### 2.2 基类接口

```python
class PnlEstimateUnit(Unit):
    version = "v0"

    def __init__(self, watching_time: float = None, watching_mds: int = None):
        # watching_time: 观察时长（秒）
        # watching_mds: 观察行情数据点个数
        pass

    def estimate(self, data, previous_result: dict = {}) -> dict:
        """
        评估交易规则在给定行情数据上的损益
        :param data: DataFrame，包含行情数据
        :return: 损益评估结果
        """
        pass
```

### 2.3 输出规范

根据 README.md，PEU 的输出包含：
- **pnl**: 每个时刻开始执行某项交易对应的收益
- **finish_time**: 本轮交易完成的时间（最后一笔交易发生的时间）

---

## 3. 核心实现

### 3.1 BtsSimplePEU - 简单的买后卖策略

**功能**：先买后卖的简单 PEU，不采用市价单拆分的模拟撮合。

**核心逻辑**：
1. **买单成交判定**：
   - 卖一价 ≤ 买单价格 → 立即成交
   - 或平均成交价 < 买单价格 → 成交

2. **卖单成交判定**：
   - 买一价 ≥ 卖单价格 → 立即成交
   - 或平均成交价 > 卖单价格 → 成交

3. **参数**：
   - `buy_shift`: 买单相对于买一价的调整单位数
   - `sell_shift`: 卖单相对于买一价的调整单位数
   - `hands`: 手数
   - `stop_loss`: 止损点数
   - `tick_size`: 最小报价单位

### 3.2 SimpleBiquotePEU - 简单双边下单

**功能**：双边同时下单，价格来自 `previous_result` 中的指定字段。

**核心逻辑**：
1. 从 `previous_result` 获取买卖价格
2. 判定买单是否成交：卖一价 ≤ 买单价格
3. 判定卖单是否成交：买一价 ≥ 卖单价格
4. 如果最后一个行情戳仍有头寸，按对手价平仓

### 3.3 BiquotePEU - 完整双边报价策略

**功能**：支持订单簿分析 + 市价单撮合模拟的完整 PEU。

**核心特性**：

1. **订单类 (Order)**：用于模拟订单执行
   ```python
   class Order:
       def check_execution(self, market_order: dict) -> dict:
           """
           判定市价单是否成交
           - 市价单价格优于订单价格则考虑成交
           - 返回成交数量和现金流
           """
   ```

2. **订单簿分析**：
   - 分析盘口前5档价格和挂单量
   - 计算同价位排单量（`volume_before_this_order`）

3. **撮合模拟**：
   - 首先根据盘口价格判定（即时成交）
   - 然后根据后续市价单判定（排队成交）
   - 支持市价单部分成交

4. **阶段控制**：
   - `order_maintaining_time`: 挂单维持时间
   - `active_closing_time`: 主动平仓时间

### 3.4 BiquoteClosePEU - 带平仓的报价策略

**功能**：在 BiquotePEU 基础上增加平仓逻辑。

**三个阶段**：
1. **报价阶段** (`start_closing_time` 之前)：正常挂单
2. **原价平仓阶段**：根据盈亏计算平仓价格
3. **对手价平仓阶段**：以对手价积极平仓

### 3.5 BiquoteStopClosePEU - 带止损的平仓策略

**功能**：在 BiquoteClosePEU 基础上增加止损机制。

**新增特性**：
- `stop_loss_ticks`: 止损tick数
- 每个行情戳检查是否触发止损
- 触发止损时立即以对手价平仓

---

## 4. 成交判定原理

### 4.1 盘口价格判定

```python
# 买单成交条件
if ask_px1 <= buy_order_price:  # 卖一价优于或等于买单价格
    buy_executed = True

# 卖单成交条件  
if bid_px1 >= sell_order_price:  # 买一价优于或等于卖单价格
    sell_executed = True
```

### 4.2 市价单撮合判定

```python
# Order.check_execution() 核心逻辑
# 1. 市价单价格更差 → 无视
if (market_order["price"] - self.price) * self.direction > 0:
    return {"volume": 0, "cash_flow": 0.0}

# 2. 考虑排单量
# 如果市价单量 > 排单量，则部分成交
```

---

## 5. 价格计算公式

### 5.1 挂单价格

```python
# 买单价格（基于买一价向下调整）
buy_order_price = round(bid_px1 - (lb - 1) * tick_size, digits)

# 卖单价格（基于卖一价向上调整）
sell_order_price = round(ask_px1 + (la - 1) * tick_size, digits)
```

其中 `lb`/`la`：
- = 1: 在一档挂单
- = 0: 比一档更优一个报价单位
- > 1: 在一档基础上加减 (lb-1) 个报价单位

### 5.2 平仓价格

```python
# 原价平仓价格
price = -round(pnl / inventory, digits)

# 对手价平仓
if inventory > 0:
    closing_px = bid_px1  # 多头平仓用买一价
else:
    closing_px = ask_px1  # 空头平仓用卖一价
```

---

## 6. 代码示例

### 6.1 使用 SimpleBiquotePEU

```python
from rbt.peu import SimpleBiquotePEU

peu = SimpleBiquotePEU(
    bid_price_key="buy_price",
    ask_price_key="sell_price", 
    watching_time=5.0,
    tick_size=0.001
)

result = peu.estimate(future_data, previous_result)
# result = {"pnl": 0.002, "buy_executed": True, ...}
```

### 6.2 使用 BiquotePEU

```python
from rbt.peu import BiquotePEU

peu = BiquotePEU(
    order_maintaining_time=5.0,
    active_closing_time=3.0,
    lb=1,  # 买一档
    la=1,  # 卖一档
    tick_size=0.005
)

result = peu.estimate(future_data)
```

---

## 7. 版本历史

| PEU 类型 | 版本 | 说明 |
|---------|------|------|
| PnlEstimateUnit | v0 | 基类 |
| BtsSimplePEU | v1 | 简单买后卖 |
| SimpleBiquotePEU | v1 | 简单双边 |
| BiquotePEU | v0 | 完整双边报价 |
| BiquoteClosePEU | v0 | 带平仓 |
| BiquoteStopClosePEU | v0 | 带止损 |

---

## 8. 总结

PEU 模块是 RBT 框架中用于**模拟交易执行和评估损益**的核心组件：

1. **职责明确**：接收 DMU 信号，输出预估损益
2. **多层次实现**：从简单到复杂，支持不同策略需求
3. **撮合模拟**：支持订单簿分析和市价单撮合
4. **灵活扩展**：通过继承 `PnlEstimateUnit` 可自定义新的 PEU

这套设计使得回测结果更接近真实交易场景，提高了策略评估的准确性。
