from .index_calculator import IndexCalculator


class RollingKlineIC(IndexCalculator):
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
