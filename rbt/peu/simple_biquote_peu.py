from .pnl_estimate_unit import PnlEstimateUnit


class SimpleBiquotePEU(PnlEstimateUnit):
    """
    简单双边下单PEU
    下单价格来自previous_result中的指定字段, 字段在初始化函数中指定.
    成交判定方式: 以买单为例, 如果卖一价格等于或低于买单的下单价格, 则认定成交.
    如果在最后一个行情戳还有头寸，则按对手价平仓。
    """

    version = "v0"

    def __init__(
        self,
        bid_price_key: str,
        ask_price_key: str,
        watching_time: float,
    ):
        """
        Args:
            bid_price_key (str): previous_result中保存买单价格的字段的key
            ask_price_key (str): previous_result中保存卖单价格的字段的key
            watching_time (float): 观察时间
        """
        super().__init__(watching_time)
        self.bid_price_key = bid_price_key
        self.ask_price_key = ask_price_key
        self.watching_time = watching_time
        self.tick_size = None
        self.digits = None

    def register_contract_info(
        self,
        symbol: str,
        tick_size: float = None,
        hands: int = None,
        digits: int = None,
    ):
        self.tick_size = tick_size
        self.digits = digits

    def get_param_str(self):
        return f"{self.bid_price_key}_{self.ask_price_key}_{self.watching_time}"

    def estimate(self, future_data) -> dict:
        # 确定报单价格
        buy_px = future_data.iloc[0][self.bid_price_key]
        sell_px = future_data.iloc[0][self.ask_price_key]
        if buy_px is None or sell_px is None:
            return {
                "pnl": 0.0,
                "buy_executed": False,
                "buy_exec_time": None,
                "sell_executed": False,
                "sell_exec_time": None,
            }

        # 准备变量
        first_md = future_data.iloc[0]
        last_md = future_data.iloc[-1]
        buy_executed = False
        buy_exec_time = None
        sell_executed = False
        sell_exec_time = None

        # 判定买单是否立即成交
        if first_md["ask_px1"] <= buy_px:
            buy_executed = True
            buy_px = first_md["ask_px1"]
            buy_exec_time = first_md.name
        else:
            buy_executable = future_data[future_data["ask_px1"] <= buy_px]
            if not buy_executable.empty:
                buy_executed = True
                buy_exec_time = buy_executable.iloc[0].name

        # 判定卖单是否立即成交
        if first_md["bid_px1"] >= sell_px:
            sell_executed = True
            sell_px = first_md["bid_px1"]
            sell_exec_time = first_md.name
        else:
            sell_executable = future_data[future_data["bid_px1"] >= sell_px]
            if not sell_executable.empty:
                sell_executed = True
                sell_exec_time = sell_executable.iloc[0].name

        # 检查最后一个行情戳是否需要平仓
        if buy_executed and not sell_executed:
            sell_px = last_md["bid_px1"]
            sell_executed = True
        elif sell_executed and not buy_executed:
            buy_px = last_md["ask_px1"]
            buy_executed = True

        # 计算损益
        pnl = 0.0
        if buy_executed and sell_executed:
            pnl = round(sell_px - buy_px, self.digits)

        return {
            "pnl": pnl,
            "buy_executed": buy_executed,
            "buy_exec_time": buy_exec_time,
            "sell_executed": sell_executed,
            "sell_exec_time": sell_exec_time,
        }
