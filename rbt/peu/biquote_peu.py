import numpy as np

from .pnl_estimate_unit import PnlEstimateUnit


def _get_volume_before_from_values(px_arr, sz_arr, order_price, side, tick_size):
    """根据订单簿计算排在本订单前面的挂单量（直接接收值数组，避免 Series 索引开销）"""
    # 挂单价超出盘口最优价（lb<=0 / la<=0），本单排在最前面
    if (side == "bid" and order_price >= px_arr[0]) or (
        side == "ask" and (px_arr[0] == 0.0 or order_price <= px_arr[0])
    ):
        return 0
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
    保留供 BiquoteClosePEU / BiquoteStopClosePEU 使用
    """

    def __init__(
        self, price: float, volume: int, direction: int, volume_before_this_order: int
    ):
        self.price = price
        self.volume = volume
        self.direction = direction
        self.volume_before_this_order = volume_before_this_order

    def check_execution(self, market_order: dict) -> dict:
        if self.volume <= 0:
            return {"volume": 0, "cash_flow": 0.0}
        if (market_order["price"] - self.price) * self.direction > 0:
            return {"volume": 0, "cash_flow": 0.0}
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
            exec_arr = future_data[exec_col].values
        else:
            exec_arr = None

        # 逐笔极值列（用于 must_not_exec 判定）
        lowest_sell_col = "MoSplitDMU_v0_auto__lowest_sell_px"
        highest_buy_col = "MoSplitDMU_v0_auto__highest_buy_px"
        has_mo_extremes = lowest_sell_col in future_data.columns
        if has_mo_extremes:
            lowest_sell_arr = future_data[lowest_sell_col].values
            highest_buy_arr = future_data[highest_buy_col].values

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
        buy_vol_before = _get_volume_before_from_values(
            bid_px_vals, bid_sz_vals, buy_order_price, "bid", self.tick_size
        )

        sell_order_price = round(
            ask_px_vals[0] + (self.la - 1) * self.tick_size, self.digits
        )
        sell_vol_before = _get_volume_before_from_values(
            ask_px_vals, ask_sz_vals, sell_order_price, "ask", self.tick_size
        )

        # 预扫描盘口极值，判断哪些单必定成交
        buy_must_exec = ask1_arr.min() <= buy_order_price
        sell_must_exec = bid1_arr.max() >= sell_order_price

        # 如果两单都必定成交，直接按挂单价成交，不用进循环
        if buy_must_exec and sell_must_exec:
            return {
                "pnl": sell_order_price - buy_order_price,
                "buy_order_executed": True,
                "sell_order_executed": True,
            }

        # 预扫描逐笔极值，判断哪些单不可能通过逐笔成交
        buy_no_chance = False
        sell_no_chance = False
        if has_mo_extremes and not buy_must_exec and n_rows > 1:
            with np.errstate(all="ignore"):
                min_sell_px = np.nanmin(lowest_sell_arr[1:])
            if np.isnan(min_sell_px) or min_sell_px > buy_order_price:
                buy_no_chance = True
        if has_mo_extremes and not sell_must_exec and n_rows > 1:
            with np.errstate(all="ignore"):
                max_buy_px = np.nanmax(highest_buy_arr[1:])
            if np.isnan(max_buy_px) or max_buy_px < sell_order_price:
                sell_no_chance = True

        # 如果两单都不可能成交（盘口没穿 + 逐笔也没机会），直接返回
        if (not buy_must_exec and buy_no_chance) and (not sell_must_exec and sell_no_chance):
            return {
                "pnl": 0.0,
                "buy_order_executed": False,
                "sell_order_executed": False,
            }

        # 逐行核对是否成交
        inventory = 0
        pnl = 0.0
        buy_order_executed = False
        sell_order_executed = False
        buy_vol_remaining = 1
        sell_vol_remaining = 1

        for i in range(n_rows):
            cur_bid1 = bid1_arr[i]
            cur_ask1 = ask1_arr[i]
            cur_time = times[i]
            time_diff = (cur_time - start_time).total_seconds()

            if time_diff <= self.order_maintaining_time:
                # 盘口价格判定成交
                if not buy_order_executed:
                    if cur_ask1 <= buy_order_price:
                        inventory += buy_vol_remaining
                        pnl -= buy_vol_remaining * buy_order_price
                        buy_order_executed = True
                if not sell_order_executed:
                    if cur_bid1 >= sell_order_price:
                        inventory -= sell_vol_remaining
                        pnl += sell_vol_remaining * sell_order_price
                        sell_order_executed = True

                # 跳过下单行；must_exec / no_chance 的单不需要逐笔判定
                if i > 0 and has_exec:
                    for mo in exec_arr[i]:
                        mo_price = mo["price"]
                        mo_vol = mo["volume"]
                        # 买单逐笔判定
                        if not buy_order_executed and not buy_must_exec and not buy_no_chance:
                            if mo_price <= buy_order_price:
                                if mo_vol <= buy_vol_before:
                                    buy_vol_before -= mo_vol
                                else:
                                    mo_vol_left = mo_vol - buy_vol_before
                                    buy_vol_before = 0
                                    cur_exec = min(buy_vol_remaining, mo_vol_left)
                                    buy_vol_remaining -= cur_exec
                                    inventory += cur_exec
                                    pnl -= buy_order_price * cur_exec
                                    if buy_vol_remaining <= 0:
                                        buy_order_executed = True
                        # 卖单逐笔判定
                        if not sell_order_executed and not sell_must_exec and not sell_no_chance:
                            if mo_price >= sell_order_price:
                                if mo_vol <= sell_vol_before:
                                    sell_vol_before -= mo_vol
                                else:
                                    mo_vol_left = mo_vol - sell_vol_before
                                    sell_vol_before = 0
                                    cur_exec = min(sell_vol_remaining, mo_vol_left)
                                    sell_vol_remaining -= cur_exec
                                    inventory -= cur_exec
                                    pnl += sell_order_price * cur_exec
                                    if sell_vol_remaining <= 0:
                                        sell_order_executed = True
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
            "sell_order_executed": sell_order_executed,
        }
