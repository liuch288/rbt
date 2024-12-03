from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC
from rbt.ic import PriceSmoothIC


class TrendDMU(DecisionMakingUnit):
    def __init__(self, period: int = 90, name: str = None):
        super().__init__(name)
        self.ma = MeanIC(period)
        self.smoother = PriceSmoothIC()
        self.last_val = 0.0

    def make_decision(self, new_data, prev_result) -> dict:
        mid = (new_data["bid_px1"] + new_data["ask_px1"]) / 2
        mid_smo = self.smoother.update(mid)
        cur_val = self.ma.update(mid_smo)
        direction = 0
        delta = cur_val - self.last_val
        if cur_val > self.last_val:
            direction = 1
        elif cur_val < self.last_val:
            direction = -1
        self.last_val = cur_val
        return {"direction": direction, "delta": delta}
