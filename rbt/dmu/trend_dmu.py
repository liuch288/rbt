from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC, SmoothIC


class TrendDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self, period: int = 90):
        super().__init__()
        self.ma = MeanIC(period)
        self.period = period
        self.smoother = SmoothIC()
        self.last_val = 0.0
        self.last_direction = 0

    def on_end_of_day(self):
        """日终重置内部 IC 和趋势状态"""
        self.ma.reset()
        self.smoother.reset()
        self.last_val = 0.0
        self.last_direction = 0

    def get_param_str(self):
        return str(self.period)

    def make_decision(self, new_data, prev_result) -> dict:
        mid = (new_data["bid_px1"] + new_data["ask_px1"]) / 2
        mid_smo = self.smoother.update(mid)
        cur_val = self.ma.update(mid_smo)
        bias = mid_smo - cur_val
        direction = 0
        delta = cur_val - self.last_val
        # 确定当前方向
        if cur_val > self.last_val:
            direction = 1
        elif cur_val < self.last_val:
            direction = -1
        self.last_val = cur_val
        # 检测方向变化
        hits = round((direction - self.last_direction) / 2.00001)
        self.last_direction = direction
        return {
            "hits": hits,
            "direction": direction,
            "delta": delta,
            "ma": cur_val,
            "bias": bias,
        }
