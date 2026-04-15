from .index_calculator import IndexCalculator


class RollingKlineIC(IndexCalculator):
    """滚动K线生成器。在滑动窗口内计算 open/close/high/low 四个值。"""
    def __init__(self, period=60):
        super().__init__(period)

    def calculate(self, new_data):
        if len(self.data) > 0:
            self.result = {
                "open": self.data[0],
                "close": self.data[-1],
                "high": max(self.data),
                "low": min(self.data),
            }
        else:
            self.result = {
                "open": new_data,
                "close": new_data,
                "high": new_data,
                "low": new_data,
            }
