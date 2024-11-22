from .decision_making_unit import DecisionMakingUnit
from ..util import get_instrument_info


class MdDMU(DecisionMakingUnit):
    def __init__(self, sym: str, name: str = None):
        super().__init__(name)
        info = get_instrument_info(sym)
        self.hands = info["hands"]

    def make_decision(self, new_data, *args, **kwargs) -> dict:
        bid_px1 = new_data["bid_px1"]
        bid_sz1 = new_data["bid_sz1"]
        ask_px1 = new_data["ask_px1"]
        ask_sz1 = new_data["ask_sz1"]
        ob_avg = (bid_px1 * ask_sz1 + ask_px1 * bid_sz1) / (bid_sz1 + ask_sz1)
        cum_avg = new_data["tot_notional"] / new_data["tot_sz"] / self.hands
        exec_avg = new_data["trade_notional"] / new_data["trade_sz"] / self.hands
        return {
            "bid": bid_px1,
            "ask": ask_px1,
            "ob_avg": ob_avg,
            "cum_avg": cum_avg,
            "exec_avg": exec_avg,
        }