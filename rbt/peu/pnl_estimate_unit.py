from ..unit import Unit


class PnlEstimateUnit(Unit):
    version = "v0"

    def __init__(self, watching_time: float = None, watching_mds: int = None):
        super().__init__()
        if watching_time is not None and watching_mds is not None:
            raise ValueError(
                "Do not input watching_time and watching_mds simultaneously"
            )
        self.watching_time = watching_time
        self.watching_mds = watching_mds

    def estimate(self, data, previous_result: dict = {}) -> dict:
        """
        评估交易规则在给定行情数据上的损益
        :param data: DataFrame，包含行情数据
        :return: 损益评估结果
        """
        pass
