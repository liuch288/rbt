from .pnl_estimate_unit import PnlEstimateUnit

class SimpleBiquotePEU(PnlEstimateUnit):
    """
    简单双边下单PEU
    下单价格来自previous_result中的指定字段, 字段在初始化函数中指定.
    成交判定方式: 以买单为例, 如果卖一价格等于或低于买单的下单价格, 则认定成交.
    """

    version = "v1"

    def __init__(
        self,
        bid_price_key: str,
        ask_price_key: str,
        watching_time,
        hands: int = 100,
        tick_size: float = 0.001,
    ):
        """
        Args:
            bid_price_key (str): previous_result中保存买单价格的字段的key
            ask_price_key (str): previous_result中保存卖单价格的字段的key
            watching_time (float): 观察时间
            hands (int): 手数
            stop_loss (int): 止损点数
            tick_size (float): 最小报价单位
        """
        super().__init__(watching_time)
        self.bid_price_key = bid_price_key
        self.ask_price_key = ask_price_key
        self.watching_time = watching_time
        self.hands = hands
        self.tick_size = tick_size

        self.digits = len(str(tick_size).split(".")[1])
        self.update_unit_name()

    def get_param_str(self):
        # TODO - 请完善这个函数
        return ""

    def estimate(self, future_data, previous_result, *args, **kwargs) -> dict:
        # 从previous_result中获取下单价格
        buy_px = previous_result[self.bid_price_key]
        sell_px = previous_result[self.ask_price_key]

        # 判定买单是否成交
        buy_executed = False
        buy_exec_time = None
        if buy_px is not None:
            buy_executable = future_data[future_data["ask_px1"] <= buy_px]
            if not buy_executable.empty:
                buy_executed = True
                buy_exec_time = buy_executable.iloc[0].name

        # 判定卖单是否成交
        sell_executed = False
        sell_exec_time = None
        if sell_px is not None:
            sell_executable = future_data[future_data["bid_px1"] >= sell_px]
            if not sell_executable.empty:
                sell_executed = True
                sell_exec_time = sell_executable.iloc[0].name

        # TODO - 加上止损逻辑

        # 计算损益
        pnl = 0
        if buy_executed and sell_executed:
            pnl = round(sell_px - buy_px, self.digits)

        return {
            "pnl": pnl,
            "buy_executed": buy_executed,
            "buy_exec_time": buy_exec_time,
            "sell_executed": sell_executed,
            "sell_exec_time": sell_exec_time,
        }
