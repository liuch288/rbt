from .decision_making_unit import DecisionMakingUnit


class MidPositionPnlDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self):
        super().__init__()
        self.positions = {}  # 用于存储之前的位置和成本

    def on_end_of_day(self):
        """日终重置持仓和现金流"""
        self.positions = {}

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        pnl_results = {}
        for key, current_position in previous_result.items():
            if key.endswith("_position"):
                position_pnl_key = key.replace("_position", "_pnl")
                if key not in self.positions:
                    self.positions[key] = {"position": 0, "cashflow": 0}

                previous_position = self.positions[key]["position"]
                mid = (new_data["bid_px1"] + new_data["ask_px1"]) / 2

                delta_position = current_position - previous_position
                trading_price = mid
                closing_price = mid

                self.positions[key]["position"] = current_position
                prev_cashflow = self.positions[key]["cashflow"]
                total_cashflow = prev_cashflow - delta_position * trading_price
                self.positions[key]["cashflow"] = total_cashflow

                pnl_results[position_pnl_key] = (
                    total_cashflow + closing_price * current_position
                )

        return pnl_results
