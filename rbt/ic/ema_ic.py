from .index_calculator import IndexCalculator


class EmaIC(IndexCalculator):
    """指数移动平均（EMA）。支持异常值检测：当新值与上一结果偏差超过 threshold 时，使用更保守的 alpha_critical 平滑。"""

    def __init__(
        self, alpha: float, threshold: float = 100.0, alpha_critical: float = 0.2
    ):
        super().__init__(1)
        self.alpha = alpha
        self.rev_alpha = 1 - alpha
        self.threshold = threshold
        self.alpha_critical = alpha_critical
        self.rev_alpha_critical = 1 - alpha_critical

    def calculate(self, new_data):
        if self.data_count <= 1:
            self.result = new_data
        else:
            if abs(new_data - self.data[0]) > self.threshold:
                self.result = (
                    new_data * self.alpha_critical
                    + self.result * self.rev_alpha_critical
                )
            else:
                self.result = new_data * self.alpha + self.result * self.rev_alpha
