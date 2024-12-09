from .decision_making_unit import DecisionMakingUnit
from ..ic import PriceSmoothIC, VarianceIC, MeanIC
from ..util import get_instrument_info


class MdDMU(DecisionMakingUnit):
    def __init__(self, sym: str, name: str = None):
        super().__init__(name)
        info = get_instrument_info(sym)
        self.hands = info["hands"]
        self.bid_filter = PriceSmoothIC()
        self.ask_filter = PriceSmoothIC()
        self.variance_ic = VarianceIC(120)
        self.mean_ic = MeanIC(120)

    def make_decision(self, new_data, *args, **kwargs) -> dict:
        bid_px1 = new_data["bid_px1"]
        bid_sz1 = new_data["bid_sz1"]
        ask_px1 = new_data["ask_px1"]
        ask_sz1 = new_data["ask_sz1"]
        total_exec = new_data["tot_sz"]
        cur_exec = new_data["trade_sz"]
        mid = (bid_px1 + ask_px1) / 2
        bid_smo = self.bid_filter.update(bid_px1)
        ask_smo = self.ask_filter.update(ask_px1)
        mid_smo = (bid_smo + ask_smo) / 2
        mean_px = round(self.mean_ic.update(mid_smo), 4)
        std = round(self.variance_ic.update(mid_smo), 9) ** 0.5
        quantile = (mid_smo - mean_px) / std if std > 1e-8 else 0
        ob_avg = (bid_px1 * ask_sz1 + ask_px1 * bid_sz1) / (bid_sz1 + ask_sz1)
        cum_avg = (
            new_data["tot_notional"] / total_exec / self.hands
            if total_exec > 0
            else None
        )
        exec_avg = (
            new_data["trade_notional"] / cur_exec / self.hands if cur_exec > 0 else None
        )
        return {
            "bid": bid_px1,
            "ask": ask_px1,
            "mid": mid,
            "mid_smo": mid_smo,
            "mean": mean_px,
            "std": std,
            "quantile": quantile,
            "ob_avg": ob_avg,
            "cum_avg": cum_avg,
            "exec_avg": exec_avg,
        }
