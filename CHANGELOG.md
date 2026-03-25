# Changelog

## [0.14] - 2026-03-25

### Changed
- `Strategy.run()`: 延迟数据加载时机，先确定需要计算的 dmu/peu，再按其 `dependencies()` 收集所需因子，按需读取避免冗余

## [0.13] - 2026-03-??
