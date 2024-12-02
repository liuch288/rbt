from rbt.ic import IndexCalculator


class PriceSmoothIC(IndexCalculator):
    """
    恒纪元: 返回恒定价
    乱纪元：返回最新价
    恒纪元: P_{t-2} = P_{t}
    乱纪元: P_{t-2} != P_{t-1} != P_{t}
    变为恒纪元: P_{t-1} == P_{t}
    """

    def __init__(self):
        super().__init__(2)
        # self.stable_era = False  # True: 恒纪元, False: 乱纪元

    def calculate(self, new_data):
        """
        当处于恒纪元时，需要三次价格都不同才进入乱纪元；
        当处于乱纪元时，只要价格连续两次相同，就进入恒纪元
        """
        if self.data[0] == self.data[1]:
            self.result = self.data[0]
        else:
            self.result = new_data
                
    def reset(self):
        super().reset()
