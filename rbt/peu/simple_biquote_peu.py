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
        stop_loss: int = 10,
        tick_size: float = 0.001,
    ):
        """
        Args:
            bid_price_key (str): previous_result中保存买单价格的字段的key
            TODO - 请补全docstring
            tick_size (float): 最小报价单位
        """
        super().__init__(watching_time)
        self.bid_price_key = bid_price_key
        self.ask_price_key = ask_price_key
        self.watching_time = watching_time
        self.tick_size = tick_size
        self.hands = hands
        self.stop_loss = stop_loss

        self.digits = len(str(tick_size).split(".")[1])
        self.update_unit_name()

    def get_param_str(self):
        return (
            f"{self.watching_time}_{self.buy_shift}_{self.sell_shift}_{self.stop_loss}"
        )

    def estimate(self, future_data, previous_result, *args, **kwargs) -> dict:
        future_data["exec_px"] = (
            future_data["trade_notional"] / future_data["trade_sz"] / self.hands
        )
        first_md = future_data.iloc[0]
        start_time = first_md.name
        buy_px = first_md["bid_px1"] + self.buy_shift * self.tick_size
        buy_px = round(buy_px, self.digits)
        sell_px = buy_px + self.sell_shift * self.tick_size
        sell_px = round(sell_px, self.digits)
        stop_losing_triggered = False

        # 判定买单是否立即成交
        first_md = future_data.iloc[0]
        if buy_px >= first_md["ask_px1"]:
            buy_px = first_md["ask_px1"]
            buy_exec_time = first_md.name
        else:
            # 判定买单是否等待后成交
            md = future_data.iloc[1:]
            md = future_data.copy()
            buy_executable = md[
                (md["ask_px1"] <= buy_px)
                | ((md["exec_px"] + self.tick_size / 2 < buy_px) & (md["trade_sz"] > 0))
            ]
            buy_exec_time = None
            if len(buy_executable) > 0:
                buy_exec_time = buy_executable.iloc[0].name

        # 如果判定卖单是否成交
        sell_exec_time = None
        if buy_exec_time is not None:
            md = future_data[future_data.index >= buy_exec_time]
            # 判定卖单是否立即成交
            first_md = md.iloc[0]
            if sell_px <= first_md["bid_px1"]:
                sell_px = first_md["bid_px1"]
                sell_exec_time = first_md.name
            else:
                sell_executable = md[
                    (md["bid_px1"] >= sell_px)
                    | (
                        (md["exec_px"] - self.tick_size / 2 > sell_px)
                        & (md["trade_sz"] > 0)
                    )
                ]
                if len(sell_executable) > 0:
                    sell_exec_time = sell_executable.iloc[0].name

        # 平仓 & 损益统计
        pnl = 0
        waiting = -1
        total_time = -1
        if (buy_exec_time is not None) and (sell_exec_time is None):
            last_md = future_data.iloc[-1]
            pnl = round(last_md["bid_px1"] - buy_px, self.digits)
        elif (buy_exec_time is not None) and (sell_exec_time is not None):
            pnl = round(sell_px - buy_px, self.digits)
            waiting = (sell_exec_time - buy_exec_time).total_seconds()
            total_time = (sell_exec_time - start_time).total_seconds()

        return {
            "pnl": pnl,
            "waiting": waiting,
            "total_time": total_time,
            "buy_exec_time": buy_exec_time,
            "sell_exec_time": sell_exec_time,
            "buy_px": buy_px,
            "sell_px": sell_px,
            "stop_losing": stop_losing_triggered,
        }
