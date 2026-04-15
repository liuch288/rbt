from .index_calculator import IndexCalculator


class DiffRateIC(IndexCalculator):
    """变化率计算器。计算 (当前值 - N期前值) / N期前值，用于收益率、涨跌幅计算等。"""

    def __init__(self, period):
        super().__init__(period)
        self.result = 0

    def calculate(self, new_data):
        if self.data_count < 2:
            self.result = 0
        else:
            old_data = self.data[0]
            if old_data != 0:
                self.result = (new_data - old_data) / old_data
            else:
                self.result = 0

    def reset(self):
        super().reset()
        self.result = 0
