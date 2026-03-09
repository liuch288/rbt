# RBT (Rule-Based Trading)

**Version:** 0.7

A lightweight, modular backtesting framework for rule-based quantitative trading strategies.

## Overview

RBT provides a flexible architecture for developing, testing, and evaluating rule-based trading strategies. It separates concerns into specialized units (DMU, PEU, IC) that can be composed freely.

## Architecture

```
Strategy
├── MdEngine      → Market Data Provider
├── DMU(s)        → Decision Making Units (generate signals)
├── PEU(s)        → PnL Estimation Units (evaluate outcomes)
└── ResultDB      → Results Storage
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **Strategy** | Main orchestration engine |
| **DMU** (DecisionMakingUnit) | Analyzes market data → generates trading signals |
| **PEU** (PnlEstimateUnit) | Estimates potential PnL for given signals |
| **MD** (MarketData Engine) | Feeds historical/streaming market data |
| **IC** (IndexCalculator) | Computes technical indicators |
| **ResultDB** | Stores and manages backtest results |

### Module Structure

```
rbt/
├── rbt/
│   ├── strategy.py      # Main Strategy class
│   ├── unit.py          # Base Unit class
│   ├── result_db.py     # Result database interface
│   ├── dmu/             # Decision Making Units
│   ├── peu/             # PnL Estimation Units
│   ├── ic/              # Index Calculators
│   ├── md/              # Market Data Engines
│   └── util/            # Utilities
├── test_rbt/            # Tests
└── setup.py             # Package configuration
```

### DMU Modules

| Module | Description |
|--------|-------------|
| `trend_dmu` | Trend-following signals |
| `mo_intention_dmu` | Market order intention detection |
| `spread_dmu` | Spread-based signals |
| `md_dmu` | Market data driven decisions |
| `pass_through_dmu` | Pass through raw tick data to ResultDB |

### PEU Modules

| Module | Description |
|--------|-------------|
| `biquote_peu` | Bid-ask spread PnL estimation |
| `biquote_close_peu` | Close price PnL estimation |
| `biquote_stop_close_peu` | Stop-loss PnL estimation |
| `bts_simple_peu` | Simple backtest PnL |

### IC Modules

| Module | Description |
|--------|-------------|
| `mean_ic` | Moving average |
| `variance_ic` | Variance/volatility |
| `rolling_kline_ic` | Rolling candlestick data |
| `sum_ic` | Cumulative sum |
| `smooth_ic` | Price smoothing |
| `first_hit_ic` | First touch detection |
| `mos_recover_ic` | MOS recovery calculation |

## Usage

### Backtest Mode

```python
from rbt import Strategy
from rbt.md import MdEngine
from rbt.dmu import TrendDMU
from rbt.peu import BiquotePEU
from rbt.result_db import ResultDB

# Initialize
strategy = Strategy()
strategy.register_md_engine(MdEngine(...))
strategy.register_dmu(TrendDMU())
strategy.register_peu(BiquotePEU())
strategy.register_result_db(ResultDB(...))

# Run backtest
strategy.run(show_progress=True)
```

### Realtime Mode

```python
from rbt import RealtimeStrategy
from rbt.dmu import TrendDMU

# Initialize
strategy = RealtimeStrategy()
strategy.register_dmu(TrendDMU())

# Process single tick
new_md = pd.Series({"price": 100, "volume": 1000})
result = strategy.run_once(new_md)
```

## Advanced Usage

### BGM (Backtest Global Parameters)

The `run()` method supports an optional `bgm` parameter for passing daily fixed parameters to all factor calculators:

```python
# Run with bgm parameters
bgm = {
    "date": "2026-03-05",
    "factor_a": 1.0,
    "factor_b": 0.5,
    "custom_field": "value"
}
strategy.run(bgm=bgm)
```

**Features:**
- `bgm` is a `dict` that defaults to `{}` (empty dict)
- BGM parameters are merged into `unit_results` on each iteration
- Both DMU and PEU can access BGM fields via `unit_results`
- Fully backward compatible (omit `bgm` for default behavior)

**Use cases:**
- Pass daily factors or parameters to all calculators
- Inject experiment variables for A/B testing
- Set date-specific constants accessible throughout the backtest
```

## Dependencies

- Python 3.x
- pandas
- progressbar2

## License

MIT

