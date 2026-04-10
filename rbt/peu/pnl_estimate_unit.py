"""
PnL 损益评估单元模块

本模块定义了 PEU (PnL Estimation Unit) 的基类，用于评估交易策略在给定行情数据上的潜在损益。

在 RBT 量化回测框架中：
- DMU (Decision Making Unit) - 分析市场数据，生成交易信号
- PEU (PnL Estimation Unit) - 评估给定信号的潜在收益

PEU 接收 DMU 产生的信号，结合历史市场数据，模拟订单执行过程，最终输出预估损益（pnl）
和交易完成时间（finish_time）。

子类继承本类实现具体的损益评估逻辑，参考实现包括：
- BtsSimplePEU: 简单的买后卖策略
- SimpleBiquotePEU: 简单双边下单
- BiquotePEU: 完整双边报价策略
- BiquoteClosePEU: 带平仓逻辑的双边报价
- BiquoteStopClosePEU: 带止损平仓的双边报价

Version:
    v0 - 初始版本
"""

from ..unit import Unit


class PnlEstimateUnit(Unit):
    """
    PnL 损益评估单元基类

    所有 PEU 类都继承自本类，实现具体的损益评估逻辑。
    本类继承自 Unit 基类，继承其名称管理和参数生成功能。

    Attributes:
        version: PEU 版本号标识
        watching_time: 观察时长（秒），与 watching_mds 二选一使用
        watching_mds: 观察行情数据点个数，与 watching_time 二选一使用

    Example:
        >>> class MyPEU(PnlEstimateUnit):
        ...     def estimate(self, future_md, future_unit_results=None):
        ...         # 实现具体的损益评估逻辑
        ...         return {"pnl": 100.0, "finish_time": 1234567890}
    """

    version = "v0"  # 版本标识

    def __init__(self, watching_time: float = None, watching_mds: int = None):
        """
        初始化 PnL 评估单元

        Args:
            watching_time: 观察时长（秒），表示从数据开头开始观察的时长。
                           与 watching_mds 参数二选一使用，不能同时指定。
            watching_mds: 观察行情数据点个数，表示从数据开头开始观察的行情数据条数。
                          与 watching_time 参数二选一使用，不能同时指定。

        Raises:
            ValueError: 当同时指定 watching_time 和 watching_mds 时抛出。
            ValueError: 当 watching_time 和 watching_mds 都未指定时抛出。

        Note:
            - watching_time 和 watching_mds 必须指定其中一个
            - 建议使用 watching_time，因为不同数据的行情频率可能不同
        """
        super().__init__()
        if watching_time is not None and watching_mds is not None:
            raise ValueError(
                "Do not input watching_time and watching_mds simultaneously"
            )
        if watching_time is None and watching_mds is None:
            raise ValueError(
                "watching_time and watching_mds cannot both be None"
            )
        self.watching_time = watching_time
        self.watching_mds = watching_mds

    def estimate(self, future_md, future_unit_results=None) -> dict:
        """
        评估交易规则在给定行情数据上的损益

        这是 PEU 的核心方法，子类需要实现具体的评估逻辑。
        方法接收未来行情数据和对应时间范围的 DMU 结果，模拟订单执行过程，返回预估的损益结果。

        Args:
            future_md: pandas.DataFrame，未来一段时间的行情数据，第一行为当前可见行情。
                       具体列结构由子类定义，通常包含价格、成交量等信息。
            future_unit_results: pandas.DataFrame，可选。index 为时间戳，columns 为因子名。
                                 时间窗口与 future_md 一致，包含 dependencies 声明的 unit 计算结果。
                                 如果 PEU 不依赖任何 unit 输出，可以为 None。

        Returns:
            dict: 损益评估结果，包含以下字段：
                - pnl (float): 预估收益，正值表示盈利，负值表示亏损
                - finish_time (int/str): 交易完成时间戳（建议返回，非必须）
                - 其他字段: 由子类定义

        Raises:
            NotImplementedError: 子类未实现此方法时抛出
        """
        raise NotImplementedError("Subclass must implement estimate() method")
