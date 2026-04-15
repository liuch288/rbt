from .index_calculator import IndexCalculator


class RangeMinIC(IndexCalculator):
    """滑动窗口最小值。在窗口内追踪最小值，窗口满后随数据滚动更新。"""

    def __init__(self, period):
        super().__init__(period)

    def calculate(self, new_data):
        pass

    def calculate_after_insertion(self):
        self.result = min(self.data)
