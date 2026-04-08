# RBT (Rule-Based Trading)

**版本：** 0.16

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

### v0.14 (2026-03-25)
- **Strategy.run() 优化**: 延迟数据加载时机，先确定 new_dmus 和 new_peus，再收集 `dependencies()` 去重后按需加载，避免冗余

### v0.13 (2026-03-25)
- **FsResultDB LSP 修复**: `skip_existing` 参数从 `save_data` 方法签名移至构造函数，符合 Liskov 替换原则
- **ResultDB 基类更新**: `save_data` 方法签名增加 `skip_existing: bool = False` 参数
- **strategy.py 重构**: `existed_data` 改名为 `loaded_data`；`existed_cols` 改名为 `existed_factors`；改用 `get_existing_factors()` 获取已有因子列表
- **strategy.py save_data**: 调用时设置 `skip_existing=True`，避免重复因子冲突
- **strategy.py TODO**: run 函数获取 loaded data 处增加 TODO，提示需指定读取哪些因子

### v0.12 (2026-03-25)
- **Unit 依赖声明**: `Unit` 基类新增 `dependencies()` 方法，返回 `list[str]`，用于声明本 unit 依赖哪些其他 unit 的结果
  - 默认返回空列表，子类按需覆写
  - `PositionPnlDMU`、`MidPositionPnlDMU` 已标注依赖 `PositionGenDMU_v0`

### v0.11 (2026-03-24)
- **合约参数统一注入**: DMU/PEU/IC 不再在构造函数中接收 `sym`、`tick_size`、`hands` 等合约参数，改为通过 `register_contract_info()` 统一注入
  - 影响: `MdDMU`、`SpreadDMU`、`MosRecoverIC`、`BiquotePEU`、`BiquoteClosePEU`、`BiquoteStopClosePEU`、`SimpleBiquotePEU`、`BtsSimplePEU`
  - `Unit` 基类的 `register_contract_info()` 默认为空操作，需要合约信息的子类自行 override
  - `Strategy.set_contract_info()` 会在注册 unit 时自动下发合约信息

### v0.10 (2026-03-20)
- **Unit 自动命名**: `Unit` 基类通过 `__init_subclass__` 自动调用 `update_unit_name()`，子类无需手动调用
- **FuturesMdEngine 简化构造**: 直接接受 `base_path` 和 `compression` 参数，无需外部创建 `FuturesDB` 实例
- **__init__ 导出补全**: `rbt.dmu` 补充导出 `KlineDMU`、`MidPositionPnlDMU`；`rbt.md` 补充导出 `FuturesMdEngine`

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
