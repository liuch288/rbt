from rbt.unit import DecisionMakingUnit


class MdDMU(DecisionMakingUnit):
    def __init__(self):
        super().__init__()

    def make_decision(self, new_data) -> dict:
        return {"bid": new_data["bid_px1"], "ask": new_data["ask_px1"]}
