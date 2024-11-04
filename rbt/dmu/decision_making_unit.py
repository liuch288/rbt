class DecisionMakingUnit:
    def __init__(self, name: str = None):
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

    def on_market_data(self, new_data, previous_result: dict = {}):
        """
        处理市场数据并返回交易决策结果
        :param new_data: 最新市场数据
        :return: 包含交易决策的字典，例如：{"decision1": 3}
        """
        return self.make_decision(new_data, previous_result)

    def make_decision(self, new_md, previous_result: dict = {}) -> dict:
        """
        根据最新的市场数据做出交易决策
        :return: 包含交易决策的字典
        """
        raise NotImplementedError("必须实现具体的决策逻辑")
