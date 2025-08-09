from collections import deque


class IndexCalculator:
    def __init__(self, period):
        self.data = deque(maxlen=period)
        self.result = None
        self.period = period
        self.data_count = 0

    def update(self, new_data):
        """
        更新数据并计算指标。
        :param data: 最新行情数据
        :return: 计算结果
        """
        self.data_count += 1
        self.calculate(new_data)
        self.data.append(new_data)
        self.calculate_after_insertion()
        return self.result

    def calculate(self, new_data):
        """
        计算指标的具体实现，需要在子类中重写。
        """
        raise NotImplementedError("Subclasses should implement this!")
    
    def calculate_after_insertion(self):
        """
        在数据插入后进行的计算，可以在子类中重写。
        """
        pass

    def reset(self):
        """
        重置calculator，清除所有数据。
        """
        self.data.clear()
        self.result = None
        self.data_count = 0
