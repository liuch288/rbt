import pandas as pd

from .pnl_estimate_unit import PnlEstimateUnit


def _detect_levels(md, max_levels=5):
    """探测行情数据中可用的档位数（至少返回1）"""
    for i in range(max_levels, 1, -1):
        key = f"bid_px{i}"
        if key in md.index and md[key] != 0.0:
            return i
    return 1


def _get_volume_before(md, order_price, side, tick_size, max_levels=5):
    """根据订单簿计算排在本订单前面的挂单量，优先利用多档行情，只有一档时退化"""
    levels = _detect_levels(md, max_levels)
    if levels <= 1:
        return md[f"{side}_sz1"]
    total_vol = 0
    for i in range(1, levels + 1):
        px = md[f"{side}_px{i}"]
        sz = md[f"{side}_sz{i}"]
        if px == 0.0:
            continue
        if side == "bid":
            if px >= order_price or abs(px - order_price) < tick_size / 2:
                total_vol += sz
        else:
            if px <= order_price or abs(px - order_price) < tick_size / 2:
                total_vol += sz
    if total_vol == 0:
        total_vol = md[f"{side}_sz1"]
    return total_vol


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
        是否成交判定不需要关心市价单方向，只要成交价格在订单之外，则忽略；相同或更优，则考虑。
        即，如果我后面的人在相同或更优的价位上发生了成交，则应该考虑这些成交量。
        return: {"volume": int, "cash_flow": float} cash_flow还需要乘以hands才能得到实际notional
        """
        # 如果当前订单已经完成，则直接返回0现金流
        if self.volume <= 0:
            return {"volume": 0, "cash_flow": 0.0}
        # 如果市价单价格更差（例如本order为买单，新的成交价格更高），则无视
        if (market_order["price"] - self.price) * self.direction > 0:
            return {"volume": 0, "cash_flow": 0.0}
        # 如果市价单价格与本单价格相同，则都考虑，不管方向（如果本单是买单，那理论上不应该有市价买单，除非本单已经被fill）
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
        return {"volume": 0, "cash_flow": 0.0}


class BiquotePEU(PnlEstimateUnit):
    version = "v0"

    def __init__(
        self,
        order_maintaining_time: float = None,
        lb: int = 1,
        la: int = 1,
    ):
        """
        lb、la是以一档为基准的价格，取1时是指在一档挂单，0时则为比一档更优一个报价单位的价格下单，其他是在一档的基础上加减lx-1个报价单位
        仅支持输入固定时长，不支持输入行情戳个数
        """
        super().__init__(order_maintaining_time, None)
        self.lb = lb
        self.la = la
        self.order_maintaining_time = order_maintaining_time
        self.tick_size = None
        self.digits = None

    def register_contract_info(self, symbol: str, tick_size: float = None, hands: int = None, digits: int = None):
        self.tick_size = tick_size
        self.digits = digits

    def get_param_str(self):
        return f"{self.order_maintaining_time}_{self.lb}_{self.la}"

    def dependencies(self):
        return ["MoSplitDMU_v0_auto"]

    def estimate(self, future_data) -> dict:
        # 确定有多少订单排在前面
        init_md = future_data.iloc[0]
        start_time = init_md.name
        # bid
        buy_order_price = round(
            init_md["bid_px1"] - (self.lb - 1) * self.tick_size, self.digits
        )
        bid_vol_at_same_level = _get_volume_before(init_md, buy_order_price, "bid", self.tick_size)
        buy_order = Order(buy_order_price, 1, 1, bid_vol_at_same_level)
        # ask
        sell_order_price = round(
            init_md["ask_px1"] + (self.la - 1) * self.tick_size, self.digits
        )
        ask_vol_at_same_level = _get_volume_before(init_md, sell_order_price, "ask", self.tick_size)
        sell_order = Order(sell_order_price, 1, -1, ask_vol_at_same_level)

        # 逐行核对是否成交
        inventory = 0
        pnl = 0.0
        # future_data_len = len(future_data)
        # 此处-3是因为最后3行要用于判定平仓价格
        buy_order_executed = False
        buy_order_exec_time = None
        sell_order_executed = False
        sell_order_exec_time = None
        is_first_row = True
        for cur_time, cur_md in future_data.iterrows():
            cur_bid1 = cur_md["bid_px1"]
            cur_ask1 = cur_md["ask_px1"]
            time_diff = (cur_time - start_time).total_seconds()
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

                # 跳过下单行的 exec_before（那是下单之前的市价单），从后续行开始判定
                if not is_first_row:
                    for mo in cur_md["MoSplitDMU_v0_auto__exec_before"]:
                        if not buy_order_executed:
                            res = buy_order.check_execution(mo)
                            if res["volume"] > 0:
                                inventory += res["volume"]
                                pnl += res["cash_flow"]
                                if buy_order.volume <= 0:
                                    buy_order_executed = True
                                    buy_order_exec_time = cur_md.name
                        if not sell_order_executed:
                            res = sell_order.check_execution(mo)
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
            is_first_row = False

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
