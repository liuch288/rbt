from .decision_making_unit import DecisionMakingUnit
from ..ic import SumIC


class NetBuyDMU(DecisionMakingUnit):
    version = "v1"

    def __init__(self, large_order_threshold: int = 10, sum_period: int = 120):
        super().__init__()
        self.large_order_threshold = large_order_threshold
        self.cumulative_net_buy = 0  # 累计净买入
        self.cumulative_large_buy = 0  # 累计大单买入
        self.cumulative_small_buy = 0  # 累计小单买入
        self.sum_period = sum_period
        self.large_sum_ic = SumIC(sum_period)
        self.small_sum_ic = SumIC(sum_period)
        self.update_unit_name()

    def get_param_str(self):
        return f"{str(self.large_order_threshold)}_{self.sum_period}"

    def make_decision(self, new_data, *args, **kwargs):
        # 计算当前统计
        current_net_buy = 0
        current_large_buy = 0
        current_small_buy = 0
        rolling_sum_large = 0
        rolling_sum_small = 0

        # 分析成交数据
        for trade in new_data["exec_before"]:
            if trade["side"] == "buy":
                current_net_buy += trade["volume"]
                if trade["volume"] >= self.large_order_threshold:
                    current_large_buy += trade["volume"]
                else:
                    current_small_buy += trade["volume"]
            elif trade["side"] == "sell":
                current_net_buy -= trade["volume"]
                if trade["volume"] >= self.large_order_threshold:
                    current_large_buy -= trade["volume"]
                else:
                    current_small_buy -= trade["volume"]

        # 更新累计统计
        self.cumulative_net_buy += current_net_buy
        self.cumulative_large_buy += current_large_buy
        self.cumulative_small_buy += current_small_buy
        rolling_sum_large = self.large_sum_ic.update(current_large_buy)
        rolling_sum_small = self.small_sum_ic.update(current_small_buy)

        # 返回统计结果
        return {
            "current_net_buy": current_net_buy,
            "cumulative_net_buy": self.cumulative_net_buy,
            "current_large_buy": current_large_buy,
            "cumulative_large_buy": self.cumulative_large_buy,
            "current_small_buy": current_small_buy,
            "cumulative_small_buy": self.cumulative_small_buy,
            "rolling_sum_large": rolling_sum_large,
            "rolling_sum_small": rolling_sum_small,
        }
