from .decision_making_unit import DecisionMakingUnit
from ..ic import SumIC


class MoIntentionDMU(DecisionMakingUnit):
    """
    市价单倾向性DMU

    统计滑动窗口内的主动买卖量，计算多空比。
    依赖 MoSplitDMU 提供的 exec_before 数据（通过 previous_result 读取）。

    输出:
        ratio: 多空比 (all_buy - all_sell) / (all_buy + all_sell)，范围 [-1, 1]
        all_buy: 窗口内累计主动买量
        all_sell: 窗口内累计主动卖量
    """

    version = "v0"

    def __init__(self, watch_mds):
        """
        Args:
            watch_mds: 滑动窗口大小（行情戳个数）
        """
        super().__init__()
        self.watch_mds = watch_mds
        self.buy_vol_ic = SumIC(watch_mds)
        self.sell_vol_ic = SumIC(watch_mds)

    def on_end_of_day(self):
        """日终重置内部 IC 状态"""
        self.buy_vol_ic.reset()
        self.sell_vol_ic.reset()

    def get_param_str(self):
        return f"{self.watch_mds}"

    def dependencies(self) -> list:
        return ["MoSplitDMU"]

    def make_decision(self, new_data, prev_result) -> dict:
        cur_mos = prev_result.get("MoSplitDMU_v0__exec_before", [])
        cur_buy = 0
        cur_sell = 0
        for mo in cur_mos:
            if mo["side"] == "buy":
                cur_buy += mo["volume"]
            elif mo["side"] == "sell":
                cur_sell += mo["volume"]
        all_buy = self.buy_vol_ic.update(cur_buy)
        all_sell = self.sell_vol_ic.update(cur_sell)

        ratio = 0.0
        all_trades = all_buy + all_sell
        if all_trades > 0:
            ratio = (all_buy - all_sell) / all_trades

        return {"ratio": ratio, "all_buy": all_buy, "all_sell": all_sell}
