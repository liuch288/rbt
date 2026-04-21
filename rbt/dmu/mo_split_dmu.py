from .decision_making_unit import DecisionMakingUnit
from ..ic import MosRecoverIC


class MoSplitDMU(DecisionMakingUnit):
    """
    市价单拆分DMU，封装MosRecoverIC，对每个行情戳计算exec_before
    """

    version = "v0"

    def __init__(self, md_type: str = "auto"):
        super().__init__()
        self.md_type = md_type
        self.recover_ic = None

    def get_param_str(self):
        return self.md_type

    def register_contract_info(
        self, symbol: str, tick_size=None, hands=None, digits=None
    ):
        self.recover_ic = MosRecoverIC(sym=symbol, md_type=self.md_type)

    def on_end_of_day(self):
        """日终重置内部 MosRecoverIC 状态"""
        if self.recover_ic is not None:
            self.recover_ic.reset()
            self.recover_ic.last_lob = None

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        if self.recover_ic is None:
            return {"exec_before": []}
        exec_before = self.recover_ic.update(new_data)
        return {"exec_before": exec_before}
