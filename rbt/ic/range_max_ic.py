from .index_calculator import IndexCalculator


class RangeMaxIC(IndexCalculator):
    """滑动窗口最大值。在窗口内追踪最大值，窗口满后随数据滚动更新。"""

    def __init__(self, period):
        super().__init__(period)

    def calculate(self, new_data):
        pass

    def calculate_after_insertion(self):
        self.result = max(self.data)
