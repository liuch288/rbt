# Changelog

## [0.13] - 2026-03-25

### Fixed
- `FsResultDB.save_data`: 修复 LSP 违规问题，`skip_existing` 参数从方法签名移至构造函数

### Changed
- `ResultDB.save_data`: 基类方法签名增加 `skip_existing: bool = False` 参数

### Added
- `strategy.py`: run 函数获取 existed data 处增加 TODO，提示需指定读取哪些因子

### Changed
- `strategy.py`: save_data 调用时设置 `skip_existing=True`，避免重复因子冲突
