from .pnl_estimate_unit import PnlEstimateUnit


class BtsSimplePEU(PnlEstimateUnit):
    """
    Buy-then-sell 先买后卖的简单PEU，不采用市价单拆分的模拟撮合，仅根据盘口报价和平均成交价判定成交
    卖一价低于或等于买单，买单成交；买一价大于或等于卖单，卖单成交。
    平均成交价低于买单，买单成交；平均成交价高于卖单，卖单成交。
    策略先下买单，买单是下单时买一价上下调整n个最小报价单位的价格，n由用户设定。
    在买单价成交后，策略才发出卖单，卖单为买一价上浮m个最小报价单位，m同样由用户设定。
    """

    version = "v1"

    def __init__(
        self,
        watching_time,
        buy_shift: int,
        sell_shift: int,
        hands: int = 100,
        stop_loss: int = 10,
        tick_size: float = 0.001,
    ):
        """
        Args:
            n (int): 买单相对于买一价的调整单位数
            m (int): 卖单相对于买一价的调整单位数
            tick_size (float): 最小报价单位
        """
        super().__init__(watching_time)
        self.watching_time = watching_time
        self.buy_shift = buy_shift
        self.sell_shift = sell_shift
        self.tick_size = tick_size
        self.hands = hands
        self.stop_loss = stop_loss

        self.digits = len(str(tick_size).split(".")[1])
        self.update_unit_name()

    def get_param_str(self):
        return (
            f"{self.watching_time}_{self.buy_shift}_{self.sell_shift}_{self.stop_loss}"
        )

    def estimate(self, future_data, *args, **kwargs) -> dict:
        future_data["mid_px"] = (future_data["bid_px1"] + future_data["ask_px1"]) / 2
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
            # 判定止损是否发生
            md = md.iloc[1:]
            stop_losing = md[md["mid_px"] < (buy_px - self.stop_loss * self.tick_size)]
            stop_losing_time = None
            if (len(stop_losing)) > 0:
                stop_losing_time = stop_losing.iloc[0].name
            if stop_losing_time is not None and sell_exec_time is not None:
                if stop_losing_time < sell_exec_time:
                    stop_losing_triggered = True
                    sell_exec_time = stop_losing_time
                    sell_px = stop_losing.iloc[0]["bid_px1"]

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
