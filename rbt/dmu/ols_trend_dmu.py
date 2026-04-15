from .decision_making_unit import DecisionMakingUnit
from ..ic import OlsTrendIC


class OlsTrendDMU(DecisionMakingUnit):
    def __init__(self, window_size: int = 60, order: int = 1):
        super().__init__()
        self.window_size = window_size
        self.order = order
        self.ols_trend_ic = OlsTrendIC(window_size, order)

    def on_end_of_day(self):
        """日终重置内部 OLS IC 状态"""
        self.ols_trend_ic.reset()

    def get_param_str(self):
        return f"{self.order}_{self.window_size}"
    
    def make_decision(self, new_data: dict, previous_result: dict = {}) -> dict:
        # Calculate the average of bid_px1 and ask_px1
        avg_price = (new_data["bid_px1"] + new_data["ask_px1"]) / 2

        # Create the input for OlsTrendIC
        input_data = {"time": new_data.name, "value": avg_price}

        # Update the OlsTrendIC
        self.ols_trend_ic.update(input_data)

        # Return the result from OlsTrendIC
        return self.ols_trend_ic.result
