from .index_calculator import IndexCalculator

class PriceFrequencyIC(IndexCalculator):
    def __init__(self, period):
        super().__init__(period)
        self.price_counts = {}

    def calculate(self, new_data):
        # 如果数据满了，去掉最旧的数据
        if len(self.data) >= self.period:
            old_data = self.data[0]
            self.price_counts[old_data] -= 1
            if self.price_counts[old_data] == 0:
                del self.price_counts[old_data]

        # 更新价格频数
        if new_data in self.price_counts:
            self.price_counts[new_data] += 1
        else:
            self.price_counts[new_data] = 1

        # 计算结果为价格频数的字典
        self.result = self.price_counts.copy()

    def reset(self):
        super().reset()
        self.price_counts.clear()
        self.result = {}
