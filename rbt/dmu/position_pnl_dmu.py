from .decision_making_unit import DecisionMakingUnit


class PositionPnlDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self):
        super().__init__()
        self.positions = {}  # 用于存储之前的位置和成本

    def on_market_data(self, new_data, previous_result: dict = {}):
        return self.make_decision(new_data, previous_result)

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        pnl_results = {}
        for key, current_position in previous_result.items():
            if key.endswith("_position"):
                position_pnl_key = key.replace("_position", "_pnl")
                if key not in self.positions:
                    self.positions[key] = {"position": 0, "cashflow": 0}

                previous_position = self.positions[key]["position"]
                cur_bid1 = new_data["bid_px1"]
                cur_ask1 = new_data["ask_px1"]

                delta_position = current_position - previous_position
                trading_price = cur_ask1 if delta_position > 0 else cur_bid1
                closing_price = cur_bid1 if current_position > 0 else cur_ask1

                self.positions[key]["position"] = current_position
                prev_cashflow = self.positions[key]["cashflow"]
                total_cashflow = prev_cashflow - delta_position * trading_price
                self.positions[key]["cashflow"] = total_cashflow

                pnl_results[position_pnl_key] = (
                    total_cashflow + closing_price * current_position
                )

        return pnl_results
