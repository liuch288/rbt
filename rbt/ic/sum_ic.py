from .index_calculator import IndexCalculator


class SumIC(IndexCalculator):
    """滑动窗口求和。在窗口内维护累计和，窗口满后增量更新。"""

    def __init__(self, period):
        super().__init__(period)
        self.result = 0

    def calculate(self, new_data):
        if self.data_count <= self.period:
            self.result += new_data
        else:
            self.result = self.result - self.data[0] + new_data

    def reset(self):
        super().reset()
        self.result = 0
