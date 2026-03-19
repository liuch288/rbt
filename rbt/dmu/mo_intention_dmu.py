from .decision_making_unit import DecisionMakingUnit
from ..ic import SumIC


class MoIntentionDMU(DecisionMakingUnit):
    """
    市价单倾向性dmu
    """

    version = "v0"

    def __init__(
        self,
        watch_mds,
        ratio_threshold,
        minimum_vol,
    ):
        """_summary_

        Args:
            watch_mds (_type_): 观测多少个行情戳
            ratio_threshold (_type_): 多空订单比的绝对值要大于的阈值
            volume_threshold: 买卖量至少要到多大才能算积极买卖
            minimum_vol: 主要方向的订单至少要达到多少才算 (以防只有1手买被当成主动买入)
        """
        super().__init__()
        self.watch_mds = watch_mds
        self.buy_vol_ic = SumIC(watch_mds)
        self.sell_vol_ic = SumIC(watch_mds)
        self.ratio_threshold = ratio_threshold
        self.minimum_vol = minimum_vol

    def get_param_str(self):
        return f"{self.watch_mds}_{self.ratio_threshold}_{self.minimum_vol}"

    def make_decision(self, new_data, prev_result) -> dict:
        cur_mos = new_data["exec_before"]
        cur_buy = 0
        cur_sell = 0
        for mo in cur_mos:
            if mo["side"] == "buy":
                cur_buy += mo["volume"]
            elif mo["side"] == "sell":
                cur_sell += mo["volume"]
        all_buy = self.buy_vol_ic.update(cur_buy)
        all_sell = self.sell_vol_ic.update(cur_sell)

        hits = 0
        ratio = 0.0
        all_trades = all_buy + all_sell
        if all_trades > 0:
            ratio = (all_buy - all_sell) / all_trades
        if all_trades > self.minimum_vol:
            if ratio > self.ratio_threshold:
                hits = 1
            elif ratio < -self.ratio_threshold:
                hits = -1

        return {"hits": hits, "ratio": ratio, "all_buy": all_buy, "all_sell": all_sell}
