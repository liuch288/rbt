from .decision_making_unit import DecisionMakingUnit


class SpreadDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self):
        super().__init__()
        self.tick_size = None

    def register_contract_info(
        self,
        symbol: str,
        tick_size: float = None,
        hands: int = None,
        digits: int = None,
    ):
        self.tick_size = tick_size

    def make_decision(self, new_data, *args, **kwargs) -> dict:
        spread = new_data["ask_px1"] - new_data["bid_px1"]
        spread = round(spread / self.tick_size)
        return {"spread": spread}
