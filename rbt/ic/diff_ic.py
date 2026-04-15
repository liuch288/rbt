from .index_calculator import IndexCalculator


class DiffIC(IndexCalculator):
    """差分计算器。计算当前值与 N 期前值的差值，用于价格变动、动量计算等。"""

    def __init__(self, period):
        super().__init__(period)
        self.result = 0

    def calculate(self, new_data):
        if self.data_count < 2:
            self.result = 0
        else:
            self.result = new_data - self.data[0]

    def reset(self):
        super().reset()
        self.result = 0
