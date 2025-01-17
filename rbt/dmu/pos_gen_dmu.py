from .decision_making_unit import DecisionMakingUnit


class PosGenDMU(DecisionMakingUnit):

    def __init__(self):
        super().__init__()
        self.rules = []

    def add_rule(self, rule_name: str, rule_detail: str, pos: int):
        self.rules.append((rule_name, rule_detail, pos))

    def make_decision(self, new_data, prev_result) -> dict:
        decision = {}
        for rule_name, rule_detail, pos in self.rules:
            try:
                if eval(rule_detail):
                    decision[f"{rule_name}_position"] = pos
                else:
                    decision[f"{rule_name}_position"] = 0
            except Exception as e:
                decision[f"{rule_name}_position"] = 0
        return decision
