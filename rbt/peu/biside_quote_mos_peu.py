import pandas as pd

from .pnl_estimate_unit import PnlEstimateUnit


class Order(object):
    """
    direction: [1] buy; [-1] sell
    """

    def __init__(
        self, price: float, volume: int, direction: int, volume_before_this_order: int
    ):
        self.price = price
        self.volume = volume
        self.direction = direction
        self.volume_before_this_order = volume_before_this_order

    def check_execution(self, market_order: dict) -> dict:
        """
        market_order: {'side': 'sell', 'price': 102.09, 'volume': 14}
        return: {"volume": int, "cash_flow": float} cash_flow还需要乘以hands才能得到实际notional
        """
        # 如果当前订单已经完成，则直接返回0现金流
        if self.volume <= 0:
            return {"volume": 0, "cash_flow": 0}
        # 如果是同向订单，则不会发生成交
        mo_direction = 1 if market_order["side"] == "buy" else -1
        if mo_direction * self.direction == 1:
            return {"volume": 0, "cash_flow": 0}
        # 只有价格匹配，才会成交
        if self.direction * (self.price - market_order["price"]) >= 0:
            mo_vol = market_order["volume"]
            if mo_vol <= self.volume_before_this_order:
                self.volume_before_this_order -= mo_vol
            else:
                mo_vol -= self.volume_before_this_order
                self.volume_before_this_order = 0
                cur_exec = min(self.volume, mo_vol)
                self.volume -= cur_exec
                cash_flow = -1 * self.direction * self.price * cur_exec
                return {"volume": cur_exec, "cash_flow": cash_flow}
        return {"volume": 0, "cash_flow": 0}


class BisideQuoteMosPEU(PnlEstimateUnit):
    def __init__(
        self,
        order_maintaining_time: float = None,
        active_closing_time: float = 3.0,
        lb: int = 1,
        la: int = 1,
        tick_size: float = 0.005,
        name: str = None,
    ):
        """
        lb、la是以一档为基准的价格，取1时是指在一档挂单，0时则为比一档更优一个报价单位的价格下单，其他是在一档的基础上加减lx-1个报价单位
        仅支持输入固定时长，不支持输入行情戳个数
        """
        super().__init__(order_maintaining_time + active_closing_time, None, name)
        self.lb = lb
        self.la = la
        self.order_maintaining_time = order_maintaining_time
        self.tick_size = tick_size
        self.digits = len(str(tick_size).split(".")[1])

    def estimate(self, future_data, *args, **kwargs) -> dict:
        # 确定有多少订单排在前面
        init_md = future_data.iloc[0]
        start_time = init_md.name
        # bid
        buy_order_price = round(
            init_md["bid_px1"] - (self.lb - 1) * self.tick_size, self.digits
        )
        bid_vol_at_same_level = 0
        for i in range(1, 6):
            cur_level_price = init_md[f"bid_px{i}"]
            cur_level_vol = init_md[f"bid_sz{i}"]
            if cur_level_price == buy_order_price:
                bid_vol_at_same_level = cur_level_vol
            elif cur_level_price < buy_order_price:
                break
        buy_order = Order(buy_order_price, 1, 1, bid_vol_at_same_level)
        # ask
        sell_order_price = round(
            init_md["ask_px1"] + (self.la - 1) * self.tick_size, self.digits
        )
        ask_vol_at_same_level = 0
        for i in range(1, 6):
            cur_level_price = init_md[f"bid_px{i}"]
            cur_level_vol = init_md[f"bid_sz{i}"]
            if cur_level_price == sell_order_price:
                ask_vol_at_same_level = cur_level_vol
            elif cur_level_price > sell_order_price:
                break
        sell_order = Order(sell_order_price, 1, -1, ask_vol_at_same_level)

        # 逐行核对是否成交
        inventory = 0
        pnl = 0.0
        future_data_len = len(future_data)
        # 此处-3是因为最后3行要用于判定平仓价格
        buy_order_executed = False
        buy_order_exec_time = None
        sell_order_executed = False
        sell_order_exec_time = None
        for i in range(future_data_len):
            cur_md = future_data.iloc[i]
            cur_bid1 = cur_md["bid_px1"]
            cur_ask1 = cur_md["ask_px1"]
            time_diff = (cur_md.name - start_time).total_seconds()
            if time_diff <= self.order_maintaining_time:
                # 首先根据盘口价格判定，看是否能立即成交 (根据盘口价格判定成交时不管量的情况)
                if not buy_order_executed:
                    if cur_ask1 <= buy_order_price:
                        inventory += buy_order.volume
                        pnl -= buy_order.volume * buy_order_price
                        buy_order_executed = True
                        buy_order_exec_time = cur_md.name
                if not sell_order_executed:
                    if cur_bid1 >= sell_order_price:
                        inventory -= sell_order.volume
                        pnl += sell_order.volume * sell_order_price
                        sell_order_executed = True
                        sell_order_exec_time = cur_md.name

                # 然后根据后续市价单判定
                for exec in cur_md["exec_after"]:
                    if not buy_order_executed:
                        res = buy_order.check_execution(exec)
                        if res["volume"] > 0:
                            inventory += res["volume"]
                            pnl += res["cash_flow"]
                            if buy_order.volume <= 0:
                                buy_order_executed = True
                                buy_order_exec_time = cur_md.name
                    if not sell_order_executed:
                        res = sell_order.check_execution(exec)
                        if res["volume"] > 0:
                            inventory -= res["volume"]
                            pnl += res["cash_flow"]
                            if sell_order.volume <= 0:
                                sell_order_executed = True
                                sell_order_exec_time = cur_md.name
                if buy_order_executed and sell_order_executed:
                    break

            else:
                if inventory == 0:
                    break
                cur_spread = round((cur_ask1 - cur_bid1) / self.tick_size)
                if cur_spread < 2:
                    break

        if inventory > 0:
            pnl += cur_bid1 * inventory
        elif inventory < 0:
            pnl += cur_ask1 * inventory

        cur_result = {
            "pnl": pnl,
            "buy_order_executed": buy_order_executed,
            "buy_order_exec_time": buy_order_exec_time,
            "sell_order_executed": sell_order_executed,
            "sell_order_exec_time": sell_order_exec_time,
        }
        return cur_result
