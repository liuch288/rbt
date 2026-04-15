from scipy.stats import pearsonr

from .index_calculator import IndexCalculator


class CorrelationIC(IndexCalculator):
    """皮尔逊相关系数计算器。计算两组数据在滑动窗口内的相关系数及 p 值。输入为 tuple，如 (price, volume)。"""

    def __init__(self, period=20):
        super().__init__(period)

    def calculate(self, new_data):
        pass

    def calculate_after_insertion(self):
        if self.data_count < self.period:
            return
        x = [s[0] for s in self.data]
        y = [s[1] for s in self.data]
        corr, p_value = pearsonr(x, y)
        self.result = {"corr": corr, "p_value": p_value}
