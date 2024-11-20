import pandas as pd
from rbt.peu.pnl_estimate_unit import PnlEstimateUnit
from rbt.peu.biquote_peu import Order


class BiquoteClosePEU(PnlEstimateUnit):
    def __init__(
        self,
        total_watching_time: float = None,
        start_closing_time: float = None,
        active_closing_time: float = 3.0,
        lb: int = 1,
        la: int = 1,
        tick_size: float = 0.005,
        name: str = None,
    ):
        """
        lb、la是以一档为基准的价格，取1时是指在一档挂单，0时则为比一档更优一个报价单位的价格下单，其他是在一档的基础上加减lx-1个报价单位
        该PEU会多要active_closing_time秒数据，如果有头寸，在这段时间内平掉。
        active_closing_time是指策略以对手价格积极平仓
        """
        super().__init__(total_watching_time + active_closing_time, None, name)
        self.total_watching_time = total_watching_time
        self.start_closing_time = start_closing_time
        self.lb = lb
        self.la = la
        self.tick_size = tick_size
        self.digits = len(str(tick_size).split(".")[1])

    def estimate(self, future_data, *args, **kwargs) -> dict:
        init_md = future_data.iloc[0]
        start_time = init_md.name
        # 确定有多少订单排在前面
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
        original_price_close = False
        closing_order = None
        for cur_time, cur_md in future_data.iterrows():
            cur_bid1 = cur_md["bid_px1"]
            cur_ask1 = cur_md["ask_px1"]
            time_diff = (cur_time - start_time).total_seconds()
            # 第一部分时间：报价
            if time_diff <= self.start_closing_time:
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
            # 第二部分时间：原价平仓或止盈平仓
            elif time_diff < self.total_watching_time:
                if inventory == 0:
                    break
                else:
                    if closing_order is None:
                        price = -round(pnl / inventory, self.digits)
                        if inventory > 0:
                            dir = -1
                            dir_str = "ask"
                            price = max(price, cur_md["bid_px1"])
                        else:
                            dir = 1
                            dir_str = "bid"
                            cur_ask1 = cur_md["ask_px1"]
                            if cur_ask1 > 0.0:
                                price = min(price, cur_ask1)
                        volume_before = 0
                        for i in range(1, 6):
                            if cur_md[f"{dir_str}_px{i}"] == price:
                                volume_before = cur_md[f"{dir_str}_sz{i}"]
                        closing_order = Order(price, abs(inventory), dir, volume_before)
                    else:
                        for exec in cur_md["exec_after"]:
                            res = closing_order.check_execution(exec)
                            if res["volume"] > 0:
                                inventory += res["volume"] * closing_order.direction
                                pnl += res["cash_flow"]
                                if inventory <= 0:
                                    original_price_close = True
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
            "original_price_close": original_price_close,
        }
        return cur_result
