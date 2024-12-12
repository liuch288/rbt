class PnlEstimateUnit(object):
    def __init__(
        self, watching_time: float = None, watching_mds: int = None, name: str = None
    ):
        if watching_time is not None and watching_mds is not None:
            raise ValueError(
                "Do not input watching_time and watching_mds simultaneously"
            )
        self.watching_time = watching_time
        self.watching_mds = watching_mds
        # set name
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

    def get_name(self)->str:
        name = f"{self.__class__.__name__}_{self.__class__.version}"
        suffix = self.get_param_str()
        if len(suffix) > 0:
            name += "_" + suffix
        return name

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
