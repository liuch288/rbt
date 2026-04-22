# RBT (Rule-Based Trading)

**版本：** 0.25

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
| `mo_intention_dmu` | 市价单倾向性分析 |
| `mo_split_dmu` | 市价单拆分（封装MosRecoverIC） |
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
| `simple_biquote_peu` | 简单双边下单盈亏 |
| `fixed_holding_peu` | 固定持有期限收益评估 |

## IC 指标计算器

| 模块 | 说明 |
|------|------|
| `mean_ic` | 简单移动平均（SMA） |
| `ema_ic` | 指数移动平均（EMA），支持异常值检测 |
| `variance_ic` | 滑动窗口方差 |
| `sum_ic` | 滑动窗口求和 |
| `diff_ic` | 差分（当前值与 N 期前值的差） |
| `diff_rate_ic` | 变化率（相对 N 期前值的百分比变化） |
| `range_min_ic` | 滑动窗口最小值 |
| `range_max_ic` | 滑动窗口最大值 |
| `min_max_ic` | 全局最小/最大值追踪 |
| `rolling_kline_ic` | 滚动K线（open/close/high/low） |
| `smooth_ic` | 价格平滑（连续相同值过滤） |
| `first_hit_ic` | 首次触及阈值检测 |
| `correlation_ic` | 皮尔逊相关系数（滑动窗口） |
| `skewness_ic` | 偏度（滑动窗口） |
| `kurtosis_ic` | 峰度（滑动窗口） |
| `ols_trend_ic` | OLS 线性回归趋势 |
| `mos_recover_ic` | 市价单还原（订单簿差分推断） |

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
- numpy
- cvxpy
- scipy
- scikit-learn
- progressbar2

## 更新日志

### v0.25 (2026-04-23)
- **MdDMU 精简**: 移除非客观衍生指标（`mid_smo`、`mean`、`std`、`quantile`）及对应的 `SmoothIC`、`VarianceIC`、`MeanIC` 依赖，仅保留直接来自行情的客观数据输出

### v0.24 (2026-04-22)
- **BiquotePEU 性能优化**: `estimate()` 方法全面重写，消除 `iterrows` 瓶颈
  - 循环前预提取 `bid_px1`、`ask_px1`、`exec_before` 为 numpy 数组，循环内通过下标直接访问
  - 预扫描盘口极值：两单都穿价时直接返回，跳过整个循环
  - 预扫描逐笔极值（`highest_buy_px`、`lowest_sell_px`）：盘口未穿且逐笔无匹配价格时跳过逐笔判定
  - 逐笔判定逻辑 inline 化，移除 `Order` 类的方法调用和 dict 构造开销
  - 移除 `exec_time` 返回字段
  - 构造函数参数不再提供默认值，必须显式传入
- **MoSplitDMU 增强**: `make_decision()` 新增 `highest_buy_px` 和 `lowest_sell_px` 两列，记录每行 exec_before 中的买卖极值价格（无成交时为 NaN），供 BiquotePEU 预判使用
- **MosRecoverIC 优化与容错**:
  - `trade_size == 1` 时跳过 cvxpy 求解，直接从均价和盘口判断方向
  - 求解失败时降级处理（`_fallback_result`）：用均价 round 到 tick_size，全量归为一笔，不再崩溃或丢失数据
  - 所有时段的求解异常均被捕获

### v0.23 (2026-04-22)
- **合约信息扩充**: `instrument_info` 从 4 个国债期货品种扩展至 87 个期货品种，覆盖 CFFEX、SHFE、DCE、CZCE、INE、GFEX 全部交易所
  - 每个品种包含 `name`（中文名）、`exchange`（交易所）、`tick_size`、`hands`（合约乘数）、`digits`（价格精度）
  - 数据来源: openctp.cn
- **代码格式化**: 全项目使用 black 格式化

### v0.22 (2026-04-17)
- **跨日运行支持（on_end_of_day）**: `Unit` 基类新增 `on_end_of_day()` 钩子方法，默认空操作，子类按需重写以重置日终状态
  - `RealtimeStrategy.on_end_of_day()` 遍历所有 DMU 执行日终逻辑
  - `KlineDMU`: 重置所有 K 线状态（open/high/low/close/volume 等）
  - `TrendDMU`: 重置 MA IC、smoother IC 及趋势方向
  - `MoIntentionDMU`: 重置买卖量 SumIC
  - `MoSplitDMU`: 重置 MosRecoverIC 及 last_lob
  - `OlsTrendDMU`: 重置 OlsTrendIC
  - `PositionGenDMU`: 重置所有 smoother IC
  - `PositionPnlDMU` / `MidPositionPnlDMU`: 清空持仓字典

### v0.21 (2026-04-16)
- **新增 IC**: DiffIC（差分）、DiffRateIC（变化率）、CorrelationIC（相关系数）、SkewnessIC（偏度）、KurtosisIC（峰度）、RangeMinIC（滑动窗口最小值）、RangeMaxIC（滑动窗口最大值）
- **PEU 排单量优化**: BiquotePEU、BiquoteClosePEU、BiquoteStopClosePEU 的排单量计算改为动态探测多档行情，优先利用可用档位累加同价位及更优价位的挂单量，仅一档时退化为 bid_sz1/ask_sz1
- **IC docstring 补全**: 所有 IC 类（含基类 IndexCalculator）补充 docstring
- **Unit version 统一**: 所有 unit 的 version 统一为 v0
- **依赖声明完善**: setup.py 补充 scipy、scikit-learn、progressbar2

### v0.20 (2026-04-11)
- **PEU estimate 签名简化**: `estimate(future_md, future_unit_results=None)` 合并为 `estimate(future_data)`
  - Strategy 在调用前通过 `pd.concat` 将行情数据与依赖的 unit 结果拼接为单一 DataFrame
  - PEU 子类只需关注一个入参，无需处理两个 DataFrame 的对齐问题
  - 无 dependencies 的 PEU 不触发拼接，零额外开销
- **所有 PEU 子类适配**: BiquotePEU、BiquoteClosePEU、BiquoteStopClosePEU、BtsSimplePEU、SimpleBiquotePEU、FixedHoldingPEU 统一更新签名和方法体变量名
- **新增 FixedHoldingPEU**: 固定持有期限收益评估，计算 pnl、long_return、short_return、max_up_vol、max_down_vol

### v0.19 (2026-04-10)
- **PEU estimate 签名重构**: `estimate(data, previous_result)` 改为 `estimate(future_md, future_unit_results=None)`
  - `future_unit_results` 为 DataFrame，时间窗口与 `future_md` 一致，包含 dependencies 声明的 unit 计算结果
  - PEU 可通过 `future_unit_results` 访问未来时段的 DMU 输出（如 `exec_before`）
- **Strategy 依赖检查**: 运行前统一检查所有 DMU/PEU 的 dependencies 是否已在 ResultDB 中，缺失则 RuntimeError 提前报错
- **Strategy PEU 调用**: 有 dependencies 的 PEU 会收到从 loaded_data 切片的 future_unit_results DataFrame
- **ResultDB.get_data()**: `factors=None` 时不再返回所有数据，改为返回 None（FsResultDB、PklResultDB 同步修改）

### v0.18 (2026-04-10)
- **MoSplitDMU / MosRecoverIC 动态档位支持**: 新增 `recover_mo_core_dynamic` 和 `detect_levels`，自动探测行情数据的可用档位数（1~5档），动态构建 volume vector
  - `md_type` 默认值从 `"lv2"` 改为 `"auto"`，自动适配不同档位的行情数据
  - 保留 `"lv1"` 和 `"lv2"` 模式用于对比
  - 价格边界仍使用二档（与 lv2 一致），仅 volume vector 利用所有可用档位
- **MoSplitDMU**: 新增 `get_param_str()`，返回 `md_type`

### v0.17 (2026-04-09)
- **MoSplitDMU**: 新增市价单拆分 DMU，将市价单恢复逻辑从 MdEngine 中剥离为独立 DMU
  - 封装 `MosRecoverIC`，支持 lv1/lv2 模式，通过 `register_contract_info` 延迟初始化
  - 仅提供 `exec_before`，不再生成 `exec_after`
- **MdEngine 精简**: 移除 `_register_raw_md` 的 `recover_mo` 参数和 `__recover_mo` 方法，行情引擎不再负责市价单拆分
- **FuturesMdEngine 精简**: 移除 `recover_mo` 构造参数和 `prepare_data` 中的市价单恢复逻辑
- **MoIntentionDMU 重构**: 从 `previous_result` 读取 `MoSplitDMU` 的输出；移除 `ratio_threshold`、`minimum_vol`、`hits`，仅输出 `ratio`、`all_buy`、`all_sell`；新增 `dependencies()` 声明对 `MoSplitDMU` 的依赖

### v0.16 (2026-04-09)
- **BiquotePEU 优化**: 移除 `active_closing_time` 参数，简化 `watching_time` 计算逻辑
- **PEU estimate 签名统一**: 所有 PEU 的 `estimate()` 方法统一增加 `previous_result=None` 默认参数
- **PEU 文档整理**: 移除旧版分析文档，更新 `rbt/peu/README.md`

### v0.15 (2026-04-09)
- **MinMaxIC**: 新增最小值/最大值追踪 IC，持续记录输入序列的全局最小值和最大值，支持 `reset()` 重置

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
