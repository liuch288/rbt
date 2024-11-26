from rbt.ic import IndexCalculator

class PriceSmoothIC(IndexCalculator):
    """
    恒纪元: 返回恒定价
    乱纪元：返回最新价
    恒纪元: P_{t-2} = P_{t}
    乱纪元: P_{t-2} != P_{t-1} != P_{t}
    变为恒纪元: P_{t-1} == P_{t}
    """
    def __init__(self, threshold):
        super().__init__(1)
        self.steady_era = False  # True: 恒纪元, False: 乱纪元
        self.steady_price = 0.0
        self.challenging_price = 0.0
        

    def calculate(self, new_data):
        if self.challenging_price == new_data:
            self.steady_era = True
            self.steady_price = new_data
        elif self.steady_price == new_data:
            self.steady_era
        
            
        self.result = self.steady_price if self.steady_era else new_data

    def reset(self):
        super().reset()
        self.steady_era = False
        self.steady_price = 0.0
        self.challenging_price = 0.0
