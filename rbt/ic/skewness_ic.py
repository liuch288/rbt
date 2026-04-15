from scipy.stats import skew

from .index_calculator import IndexCalculator


class SkewnessIC(IndexCalculator):
    """偏度计算器。衡量滑动窗口内数据分布的不对称程度。>0 右偏，<0 左偏，≈0 对称。"""

    def __init__(self, period=20):
        super().__init__(period)

    def calculate(self, new_data):
        pass

    def calculate_after_insertion(self):
        if self.data_count < self.period:
            return
        self.result = skew(self.data, bias=False)
