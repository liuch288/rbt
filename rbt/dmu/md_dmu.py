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
        cur_notional = new_data["trade_notional"]
        cur_exec = new_data["trade_sz"]
        bid_smo = self.bid_filter.update(bid_px1)
        ask_smo = self.ask_filter.update(ask_px1)
        mid = (bid_smo + ask_smo) / 2
        mean_px = round(self.mean_ic.update(mid), 4)
        std = round(self.variance_ic.update(mid), 9) ** 0.5
        quantile = (mid - mean_px) / std if std > 1e-8 else 0
        ob_avg = (bid_px1 * ask_sz1 + ask_px1 * bid_sz1) / (bid_sz1 + ask_sz1)
        cum_avg = new_data["tot_notional"] / new_data["tot_sz"] / self.hands
        exec_avg = cur_notional / cur_exec / self.hands if cur_exec > 0 else 0
        return {
            "bid": bid_px1,
            "ask": ask_px1,
            "mid_smo": mid,
            "mean": mean_px,
            "std": std,
            "quantile": quantile,
            "ob_avg": ob_avg,
            "cum_avg": cum_avg,
            "exec_avg": exec_avg,
        }