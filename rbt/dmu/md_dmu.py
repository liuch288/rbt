from .decision_making_unit import DecisionMakingUnit


class MdDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self):
        super().__init__()
        self.hands = None
        self._prev_oi = None

    def register_contract_info(
        self,
        symbol: str,
        tick_size: float = None,
        hands: int = None,
        digits: int = None,
    ):
        self.hands = hands

    def make_decision(self, new_data, *args, **kwargs) -> dict:
        bid_px1 = new_data["bid_px1"]
        bid_sz1 = new_data["bid_sz1"]
        ask_px1 = new_data["ask_px1"]
        ask_sz1 = new_data["ask_sz1"]
        total_exec = new_data["tot_sz"]
        cur_exec = new_data["trade_sz"]
        mid = (bid_px1 + ask_px1) / 2
        ob_avg = (bid_px1 * ask_sz1 + ask_px1 * bid_sz1) / (bid_sz1 + ask_sz1)
        cum_avg = (
            new_data["tot_notional"] / total_exec / self.hands
            if total_exec > 0
            else None
        )
        exec_avg = (
            new_data["trade_notional"] / cur_exec / self.hands if cur_exec > 0 else None
        )
        prev_oi = self._prev_oi
        oi_change = new_data["oi"] - prev_oi if prev_oi is not None else 0
        self._prev_oi = new_data["oi"]

        return {
            "bid": bid_px1,
            "ask": ask_px1,
            "mid": mid,
            "volume": cur_exec,
            "oi_diff": oi_change,
            "ob_avg": ob_avg,
            "cum_avg": cum_avg,
            "exec_avg": exec_avg,
        }
