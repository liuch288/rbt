class PnlEstimateUnit:
    version = "v0"

    def __init__(self, watching_time: float = None, watching_mds: int = None):
        if watching_time is not None and watching_mds is not None:
            raise ValueError(
                "Do not input watching_time and watching_mds simultaneously"
            )
        self.watching_time = watching_time
        self.watching_mds = watching_mds
        self.name = f"{self.__class__.__name__}_{self.__class__.version}"

    def update_unit_name(self) -> str:
        """根据参数更新unit name，由各个PEU主动调用"""
        suffix = self.get_param_str()
        if len(suffix) > 0:
            self.name += "_" + suffix

    def get_param_str(self) -> str:
        """生成参数信息，默认为空

        使用【unit名称-版本号-参数信息】构成PEU唯一标识。
        对于无参数PEU，子类不需要实现，默认为空。而如果有参数配置，则需要实现参数信息生成函数。

        Returns:
            str: 载明参数的字符串
        """
        return ""

    def estimate(self, data, previous_result: dict = {}) -> dict:
        """
        评估交易规则在给定行情数据上的损益
        :param data: DataFrame，包含行情数据
        :return: 损益评估结果
        """
        pass
