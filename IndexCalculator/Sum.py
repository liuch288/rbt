from .IndexCalculator import IndexCalculator


class Sum(IndexCalculator):
    def __init__(self, period):
        super().__init__(period)
        self.result = 0  # Initialize result to zero to represent the sum

    def calculate(self, new_data):
        if self.data_count <= self.period:
            self.result += new_data
        else:
            self.result = self.result - self.data[0] + new_data
