from .decision_making_unit import DecisionMakingUnit
from ..ic import SmoothIC


class PositionGenDMU(DecisionMakingUnit):

    def __init__(self):
        super().__init__()
        self.rules = []
        self.smoother = {}

    def add_rule(self, rule_name: str, rule_detail: str, target_position: int, smooth: bool=False):
        self.rules.append((rule_name, rule_detail, target_position, smooth))
        if smooth:
            self.smoother[rule_name] = SmoothIC()

    def make_decision(self, new_data, prev_result) -> dict:
        decision = {}
        for rule_name, rule_detail, target_position, smooth in self.rules:
            position = 0
            try:
                if eval(rule_detail):
                    position = target_position
            except Exception as e:
                pass
            if smooth:
                position = self.smoother[rule_name].update(position)    
            decision[f"{rule_name}_position"] = position
        return decision
