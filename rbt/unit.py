class Unit(object):
    def __init__(self) -> None:
        self.name = f"{self.__class__.__name__}_{self.__class__.version}"
        self.name_updated = False

    def update_unit_name(self) -> str:
        """根据参数更新unit name，由各个unit主动调用"""
        suffix = self.get_param_str()
        if len(suffix) > 0:
            self.name += "_" + suffix
        self.name_updated = True

    def get_param_str(self) -> str:
        """生成参数信息，默认为空

        使用【unit名称-版本号-参数信息】构成PEU唯一标识。
        对于无参数PEU，子类不需要实现，默认为空。而如果有参数配置，则需要实现参数信息生成函数。

        Returns:
            str: 载明参数的字符串
        """
        return ""
