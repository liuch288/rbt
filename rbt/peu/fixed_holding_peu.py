"""
固定持有期限收益评估单元 (FixedHoldingPEU)

本模块定义了 FixedHoldingPEU 类，用于评估固定持有期限的收益情况。
该 PEU 计算从数据起点到终点的收益，以及周期内的最大波幅。

依赖 MdDMU 提供的中间价 (mid)。

计算指标（均为绝对价差，单位：原始价格单位）：
1. mid_long_pnl: 中间价做多 = 最后中间价 - 第一中间价
2. mid_short_pnl: 中间价做空 = 第一中间价 - 最后中间价
3. cross_long_pnl: 对手价做多 = 最后bid - 第一个ask
4. cross_short_pnl: 对手价做空 = 第一个bid - 最后ask
5. mid_max_up: 中间价最大上行 = 周期内mid最高值 - 第一中间价
6. mid_max_down: 中间价最大下行 = 第一中间价 - 周期内mid最低值
7. cross_max_up: 对手价最大上行 = 周期内bid最高值 - 第一个ask
8. cross_max_down: 对手价最大下行 = 第一个bid - 周期内ask最低值

中间价来自 MdDMU 的 mid 字段
最高价 = mid 最大值
最低价 = mid 最小值

Version:
    v0 - 初始版本
"""

from .pnl_estimate_unit import PnlEstimateUnit


class FixedHoldingPEU(PnlEstimateUnit):
    """
    固定持有期限收益评估单元

    中间价来自 MdDMU 的 mid 字段。
    """

    version = "v0"

    def __init__(self, watching_time: float = None, watching_mds: int = None):
        super().__init__(watching_time=watching_time, watching_mds=watching_mds)

    def dependencies(self):
        return ["MdDMU_v0"]

    def estimate(self, future_data) -> dict:
        if future_data is None or len(future_data) == 0:
            raise ValueError("数据不能为空")

        required_columns = ["ask_px1", "bid_px1", "MdDMU_v0__mid"]
        for col in required_columns:
            if col not in future_data.columns:
                raise ValueError(f"数据中缺少必要列: {col}")

        first_data = future_data.iloc[0]
        last_data = future_data.iloc[-1]

        first_ask = first_data["ask_px1"]
        first_bid = first_data["bid_px1"]
        last_ask = last_data["ask_px1"]
        last_bid = last_data["bid_px1"]

        period_high = future_data["MdDMU_v0__mid"].max()
        period_low = future_data["MdDMU_v0__mid"].min()

        first_mid_px = first_data["MdDMU_v0__mid"]
        last_mid_px = last_data["MdDMU_v0__mid"]

        mid_long_pnl = last_mid_px - first_mid_px
        mid_short_pnl = first_mid_px - last_mid_px
        cross_long_pnl = last_bid - first_ask
        cross_short_pnl = first_bid - last_ask
        mid_max_up = period_high - first_mid_px
        mid_max_down = first_mid_px - period_low
        cross_max_up = future_data["bid_px1"].max() - first_ask
        cross_max_down = first_bid - future_data["ask_px1"].min()

        return {
            "mid_long_pnl": mid_long_pnl,
            "mid_short_pnl": mid_short_pnl,
            "cross_long_pnl": cross_long_pnl,
            "cross_short_pnl": cross_short_pnl,
            "mid_max_up": mid_max_up,
            "mid_max_down": mid_max_down,
            "cross_max_up": cross_max_up,
            "cross_max_down": cross_max_down,
        }

    def get_param_str(self) -> str:
        if self.watching_mds is not None:
            return f"{self.watching_mds}t"
        elif self.watching_time is not None:
            return f"{self.watching_time}s"
        else:
            raise ValueError("watching_time and watching_mds are not set")
