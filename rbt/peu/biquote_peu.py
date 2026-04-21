from .pnl_estimate_unit import PnlEstimateUnit


def _get_volume_before_from_values(px_arr, sz_arr, order_price, side, tick_size):
    """根据订单簿计算排在本订单前面的挂单量（直接接收值数组，避免 Series 索引开销）"""
    # 探测可用档位数
    levels = 1
    for i in range(len(px_arr) - 1, 0, -1):
        if px_arr[i] != 0.0:
            levels = i + 1
            break
    if levels <= 1:
        return sz_arr[0]
    total_vol = 0
    for i in range(levels):
        px = px_arr[i]
        sz = sz_arr[i]
        if px == 0.0:
            continue
        if side == "bid":
            if px >= order_price or abs(px - order_price) < tick_size / 2:
                total_vol += sz
        else:
            if px <= order_price or abs(px - order_price) < tick_size / 2:
                total_vol += sz
    if total_vol == 0:
        total_vol = sz_arr[0]
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
    version = "v1"

    def __init__(
        self,
        order_maintaining_time: float,
        lb: int,
        la: int,
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
        return f"{self.order_maintaining_time}_{self.lb}_{self.la}"

    def dependencies(self):
        return ["MoSplitDMU_v0_auto"]

    def estimate(self, future_data) -> dict:
        n_rows = len(future_data)
        # 预提取所有需要的列为 numpy 数组 / list，避免循环内 Series 开销
        times = future_data.index
        bid1_arr = future_data["bid_px1"].values
        ask1_arr = future_data["ask_px1"].values
        exec_col = "MoSplitDMU_v0_auto__exec_before"
        has_exec = exec_col in future_data.columns
        if has_exec:
            exec_arr = future_data[exec_col].values  # object array of lists
        else:
            exec_arr = None

        start_time = times[0]

        # 从第一行提取初始盘口，计算挂单价格和排队量
        init_row = future_data.iloc[0]
        max_levels = 5
        bid_px_vals = [init_row.get(f"bid_px{i+1}", 0.0) for i in range(max_levels)]
        bid_sz_vals = [init_row.get(f"bid_sz{i+1}", 0.0) for i in range(max_levels)]
        ask_px_vals = [init_row.get(f"ask_px{i+1}", 0.0) for i in range(max_levels)]
        ask_sz_vals = [init_row.get(f"ask_sz{i+1}", 0.0) for i in range(max_levels)]

        buy_order_price = round(
            bid_px_vals[0] - (self.lb - 1) * self.tick_size, self.digits
        )
        bid_vol_before = _get_volume_before_from_values(
            bid_px_vals, bid_sz_vals, buy_order_price, "bid", self.tick_size
        )
        buy_order = Order(buy_order_price, 1, 1, bid_vol_before)

        sell_order_price = round(
            ask_px_vals[0] + (self.la - 1) * self.tick_size, self.digits
        )
        ask_vol_before = _get_volume_before_from_values(
            ask_px_vals, ask_sz_vals, sell_order_price, "ask", self.tick_size
        )
        sell_order = Order(sell_order_price, 1, -1, ask_vol_before)

        # 逐行核对是否成交
        inventory = 0
        pnl = 0.0
        buy_order_executed = False
        buy_order_exec_time = None
        sell_order_executed = False
        sell_order_exec_time = None
        cur_bid1 = bid1_arr[0]
        cur_ask1 = ask1_arr[0]

        for i in range(n_rows):
            cur_bid1 = bid1_arr[i]
            cur_ask1 = ask1_arr[i]
            cur_time = times[i]
            time_diff = (cur_time - start_time).total_seconds()

            if time_diff <= self.order_maintaining_time:
                # 盘口价格判定成交
                if not buy_order_executed:
                    if cur_ask1 <= buy_order_price:
                        inventory += buy_order.volume
                        pnl -= buy_order.volume * buy_order_price
                        buy_order_executed = True
                        buy_order_exec_time = cur_time
                if not sell_order_executed:
                    if cur_bid1 >= sell_order_price:
                        inventory -= sell_order.volume
                        pnl += sell_order.volume * sell_order_price
                        sell_order_executed = True
                        sell_order_exec_time = cur_time

                # 跳过下单行的 exec_before，从后续行开始判定
                if i > 0 and has_exec:
                    for mo in exec_arr[i]:
                        if not buy_order_executed:
                            res = buy_order.check_execution(mo)
                            if res["volume"] > 0:
                                inventory += res["volume"]
                                pnl += res["cash_flow"]
                                if buy_order.volume <= 0:
                                    buy_order_executed = True
                                    buy_order_exec_time = cur_time
                        if not sell_order_executed:
                            res = sell_order.check_execution(mo)
                            if res["volume"] > 0:
                                inventory -= res["volume"]
                                pnl += res["cash_flow"]
                                if sell_order.volume <= 0:
                                    sell_order_executed = True
                                    sell_order_exec_time = cur_time
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

        return {
            "pnl": pnl,
            "buy_order_executed": buy_order_executed,
            "buy_order_exec_time": buy_order_exec_time,
            "sell_order_executed": sell_order_executed,
            "sell_order_exec_time": sell_order_exec_time,
        }
