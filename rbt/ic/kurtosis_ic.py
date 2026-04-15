from scipy.stats import kurtosis

from .index_calculator import IndexCalculator


class KurtosisIC(IndexCalculator):
    """峰度计算器。衡量滑动窗口内数据分布的尖峭或平坦程度。>0 尖峰（厚尾），<0 平坦（薄尾），≈0 近似正态。"""

    def __init__(self, period=20):
        super().__init__(period)

    def calculate_after_insertion(self):
        if self.data_count < self.period:
            return
        self.result = kurtosis(self.data, bias=False)
