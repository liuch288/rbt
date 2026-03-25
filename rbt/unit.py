class Unit(object):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        original_init = cls.__dict__.get("__init__")
        if original_init is not None:
            import functools

            @functools.wraps(original_init)
            def wrapped_init(self, *args, **kw):
                is_outermost = not hasattr(self, "_unit_initializing")
                if is_outermost:
                    self._unit_initializing = True
                original_init(self, *args, **kw)
                if is_outermost:
                    del self._unit_initializing
                    if not self.name_updated:
                        self.update_unit_name()

            cls.__init__ = wrapped_init

    def __init__(self) -> None:
        self.name = f"{self.__class__.__name__}_{self.__class__.version}"
        self.name_updated = False
        self.contract_info = None

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

    def dependencies(self) -> list:
        """返回本 unit 依赖的其他因子名称列表

        Returns:
            list[str]: 依赖的因子名称，如 ["MdDMU_v0", "KlineDMU_v0_5min"]
        """
        return []

    def register_contract_info(self, symbol: str, tick_size: float = None, hands: int = None, digits: int = None):
        """注册合约信息

        Args:
            symbol: 合约代码
            tick_size: 最小变动价位
            hands: 合约乘数
            digits: 价格精度
        """
        self.contract_info = {
            "symbol": symbol,
            "tick_size": tick_size,
            "hands": hands,
            "digits": digits,
        }

