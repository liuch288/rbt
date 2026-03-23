from .decision_making_unit import DecisionMakingUnit
from ..ic import SmoothIC, VarianceIC, MeanIC


class MdDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self):
        super().__init__()
        self.hands = None
        self.bid_filter = SmoothIC()
        self.ask_filter = SmoothIC()
        self.variance_ic = VarianceIC(120)
        self.mean_ic = MeanIC(120)

    def register_contract_info(self, symbol: str, tick_size: float = None, hands: int = None, digits: int = None):
        self.hands = hands

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
        mean_px = self.mean_ic.update(mid_smo)
        variance = self.variance_ic.update(mid_smo)
        std = variance**0.5 if variance > 0 else 0
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
