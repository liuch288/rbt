from .index_calculator import IndexCalculator


class SmoothIC(IndexCalculator):
    """
    连续两个相同的，就返回原始值；其他情况，返回最新值。
    """

    def __init__(self):
        super().__init__(2)

    def calculate(self, new_data):
        if self.data_count < 3:
            self.result = new_data
            return None
        if self.data[0] == self.data[1]:
            self.result = self.data[0]
        else:
            self.result = new_data
