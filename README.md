# RBT (Rule-Based Trading)

**版本：** 0.8

RBT 是一个轻量级、模块化的规则型量化交易策略回测框架。

## 简介

RBT 提供灵活的架构，用于开发、测试和评估规则型交易策略。框架将功能分离为专门的单元（DMU、PEU、IC），可以自由组合使用。

## 架构

```
Strategy
├── MdEngine      → 市场数据引擎
├── DMU(s)        → 决策单元（生成信号）
├── PEU(s)        → 盈亏估算单元（评估结果）
└── ResultDB      → 结果数据库
```

### 核心组件

| 组件 | 说明 |
|------|------|
| **Strategy** | 主策略引擎，负责 orchestrate 各单元 |
| **DMU** (DecisionMakingUnit) | 分析市场数据 → 生成交易信号 |
| **PEU** (PnlEstimateUnit) | 根据信号估算潜在盈亏 |
| **MD** (MarketData Engine) | 提供历史/实时市场数据 |
| **IC** (IndexCalculator) | 计算技术指标 |
| **ResultDB** | 存储和管理回测结果 |

## 模块结构

```
rbt/
├── rbt/
│   ├── strategy.py           # 主策略类
│   ├── unit.py               # 基础单元类
│   ├── realtime_strategy.py  # 实时策略类
│   ├── result_db/            # 结果数据库（v0.8 新结构）
│   │   ├── __init__.py
│   │   ├── result_db.py      # ResultDB 抽象基类
│   │   └── pkl_result_db.py  # PklResultDB 实现
│   ├── dmu/                  # 决策单元
│   ├── peu/                  # 盈亏估算单元
│   ├── ic/                   # 指标计算器
│   ├── md/                   # 市场数据引擎
│   └── util/                 # 工具函数
├── test_rbt/                 # 测试用例
└── setup.py                  # 包配置
```

## DMU 决策单元

| 模块 | 说明 |
|------|------|
| `trend_dmu` | 趋势跟踪信号 |
| `mo_intention_dmu` | 市单意图检测 |
| `spread_dmu` | 价差信号 |
| `md_dmu` | 市场数据驱动决策 |
| `pass_through_dmu` | 透传原始tick数据到ResultDB |

## PEU 盈亏估算单元

| 模块 | 说明 |
|------|------|
| `biquote_peu` | 买卖价差盈亏估算 |
| `biquote_close_peu` | 收盘价盈亏估算 |
| `biquote_stop_close_peu` | 止损盈亏估算 |
| `bts_simple_peu` | 简单回测盈亏 |

## IC 指标计算器

| 模块 | 说明 |
|------|------|
| `mean_ic` | 移动平均 |
| `variance_ic` | 方差/波动率 |
| `rolling_kline_ic` | 滚动K线数据 |
| `sum_ic` | 累计求和 |
| `smooth_ic` | 价格平滑 |
| `first_hit_ic` | 首次触及检测 |
| `mos_recover_ic` | MOS恢复计算 |

## 使用示例

### 回测模式

```python
from rbt import Strategy
from rbt.md import MdEngine
from rbt.dmu import TrendDMU
from rbt.peu import BiquotePEU
from rbt.result_db import PklResultDB

# 初始化
strategy = Strategy()
strategy.register_md_engine(MdEngine(...))
strategy.register_dmu(TrendDMU())
strategy.register_peu(BiquotePEU())
strategy.register_result_db(PklResultDB(...))

# 运行回测
strategy.run(show_progress=True)
```

### 实时模式

```python
from rbt import RealtimeStrategy
from rbt.dmu import TrendDMU

# 初始化
strategy = RealtimeStrategy()
strategy.register_dmu(TrendDMU())

# 处理单条tick
new_md = pd.Series({"price": 100, "volume": 1000})
result = strategy.run_once(new_md)
```

## 高级用法

### BGM（Backtest Global Parameters）

`run()` 方法支持可选的 `bgm` 参数，用于向所有因子计算器传递每日固定参数：

```python
# 使用 bgm 参数运行
bgm = {
    "date": "2026-03-05",
    "factor_a": 1.0,
    "factor_b": 0.5,
    "custom_field": "value"
}
strategy.run(bgm=bgm)
```

**特性：**
- `bgm` 是 `dict`，默认为 `{}`（空字典）
- BGM 参数会在每次迭代时合并到 `unit_results` 中
- DMU 和 PEU 都可通过 `unit_results` 访问 BGM 字段
- 完全向后兼容（省略 `bgm` 则使用默认行为）

**使用场景：**
- 向所有计算器传递每日因子或参数
- 注入实验变量用于 A/B 测试
- 设置日期特定常量，在整个回测过程中可访问

### ResultDB 用法（v0.8）

```python
from rbt.result_db import PklResultDB

# 初始化
db = PklResultDB("/path/to/db_directory")

# 保存数据
db.save_data("AAPL", datetime.date(2026, 3, 18), df)

# 读取全部数据
data = db.get_data("AAPL", datetime.date(2026, 3, 18))

# 读取指定因子（支持前缀匹配）
# 例如 factors=["price_", "volume_"] 会匹配所有以这些前缀开头的列
data = db.get_data("AAPL", datetime.date(2026, 3, 18), factors=["price_", "vol"])
```

**v0.8 更新说明：**
- `ResultDB` 已重构为抽象基类（ABC）
- `PklResultDB` 是基于 pickle 的默认实现
- `get_data()` 新增 `factors` 参数，支持前缀匹配
- 向后兼容：导入方式保持不变

## 依赖

- Python 3.x
- pandas
- progressbar2

## 更新日志

### v0.8 (2026-03-18)
- **ResultDB 重构**: 提取抽象基类，支持多种存储后端
  - 新增 `rbt/result_db/` 文件夹结构
  - `ResultDB` 改为抽象基类 (`ABC`)
  - `PklResultDB` 作为 pickle 实现
  - 向后兼容: `from rbt.result_db import ResultDB` 保持不变
- **ResultDB.get_data() 新增 factors 参数**: 支持前缀匹配读取指定因子
- **类型注解修复**: `_get_path` 返回类型从 `pd.DataFrame` 改为 `str`
- **.gitignore**: 移除 `pkl_*` 规则

## 许可证

MIT
