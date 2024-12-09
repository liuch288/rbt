from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC, PriceSmoothIC


class TrendDMU(DecisionMakingUnit):
    def __init__(self, period: int = 90, name: str = None):
        super().__init__(name)
        self.ma = MeanIC(period)
        self.smoother = PriceSmoothIC()
        self.last_val = 0.0
        self.last_direction = 0

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
