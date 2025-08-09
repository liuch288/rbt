from .index_calculator import IndexCalculator
from .mean_ic import MeanIC


class VarianceIC(IndexCalculator):
    def __init__(self, period):
        super().__init__(1)
        self.exp_squared = MeanIC(period)  # 用于计算平方的期望
        self.exp = MeanIC(period)  # 用于计算期望

    def calculate(self, new_data):
        """
        方差 = 平方的期望 - 期望的平方
        """
        exp_of_squared_val = self.exp_squared.update(new_data*new_data)
        exp_val = self.exp.update(new_data)
        squared_exp_val = exp_val * exp_val
        self.result = exp_of_squared_val - squared_exp_val
