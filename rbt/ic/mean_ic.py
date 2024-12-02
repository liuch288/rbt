from .index_calculator import IndexCalculator


class MeanIC(IndexCalculator):
    def __init__(self, period):
        super().__init__(period)
        self.sum = 0  # 累计值

    def calculate(self, new_data):
        """
        计算简单移动平均。
        :param new_data: 最新行情数据
        """
        if self.data_count <= self.period:
            # 当数据个数小于period时，直接累加
            self.sum += new_data
            self.result = self.sum / self.data_count
        else:
            # 当数据个数等于period时，使用累计值更新
            self.sum += new_data - self.data[0]
            self.result = self.sum / self.period