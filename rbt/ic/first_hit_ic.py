from .index_calculator import IndexCalculator


class FirstHitIC(IndexCalculator):
    def __init__(self, threshold):
        super().__init__(1)
        self.threshold = abs(threshold)
        self.result = 0
        self.has_hit_threshold = False  # 标记是否已经触发过阈值

    def calculate(self, new_data):
        # 如果变动次数回到0，则重置触发标记
        if new_data == 0:
            self.has_hit_threshold = False

        # 如果还没有触发过阈值，且新的变动次数绝对值达到或超过阈值
        if not self.has_hit_threshold and abs(new_data) >= self.threshold:
            self.result = 1 if new_data > 0 else -1
            self.has_hit_threshold = True  # 标记为已触发
        else:
            self.result = 0

    def reset(self):
        super().reset()
        self.result = 0
        self.has_hit_threshold = False  # 重置触发标记
