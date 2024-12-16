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
        for key, value in previous_result.items():
            if key.endswith("_position"):
                position_pnl_key = key.replace("_position", "_pnl")
                if key not in self.positions:
                    self.positions[key] = {'position': 0, 'cost': 0}
                
                current_position = self.positions[key]['position']
                previous_position = value
                if current_position != previous_position:
                    if current_position != 0:
                        # 平仓
                        if current_position == 1:
                            close_price = new_data["bid_px1"]
                        else:
                            close_price = new_data["ask_px1"]
                        pnl = close_price - self.positions[key]['cost']
                        self.positions[key]['position'] = 0
                    # 开仓
                    if previous_position != 0:
                        if previous_position == 1:
                            open_price = new_data["ask_px1"]
                        else:
                            open_price = new_data["bid_px1"]
                        self.positions[key]['cost'] = open_price
                        self.positions[key]['position'] = previous_position
                    
                    pnl_results[position_pnl_key] = pnl
                else:
                    # 没有变动，损益为0
                    pnl_results[position_pnl_key] = 0
        
        return pnl_results
