import cvxpy as cp
import numpy as np

from .index_calculator import IndexCalculator
from ..util import get_instrument_info


def recover_mo_core_lv2(
    last_lob, cur_lob, tick_size: float, hands: int, split_unknown: bool
) -> list:
    """
    使用bid2至ask2的价位猜成交
    """
    trade_notional = cur_lob["trade_notional"]
    trade_size = cur_lob["trade_sz"]
    if trade_size == 0:
        return []
    avg_price = trade_notional / trade_size / hands
    tick_notional = round(tick_size * hands)
    last_mid_px = (last_lob["bid_px1"] + last_lob["ask_px1"]) / 2
    if avg_price < last_mid_px:
        avg_price_boundary = (int(avg_price / tick_size) - 1) * tick_size
    else:
        avg_price_boundary = (int(avg_price / tick_size) + 2) * tick_size

    # price vector
    last_bid2 = 9999999 if last_lob["bid_px2"] == 0.0 else last_lob["bid_px2"]
    cur_bid2 = 9999999 if cur_lob["bid_px2"] == 0.0 else cur_lob["bid_px2"]
    min_price = min(last_bid2, avg_price_boundary, cur_bid2)
    min_price_notional = round(min_price * hands)
    last_ask2 = 0 if last_lob["ask_px2"] == 0.0 else last_lob["ask_px2"]
    cur_ask2 = 0 if cur_lob["ask_px2"] == 0.0 else cur_lob["ask_px2"]
    max_price = max(last_ask2, avg_price_boundary, cur_ask2)
    max_price_notional = round(max_price * hands)
    bids = list(
        range(min_price_notional, round(last_lob["bid_px1"] * hands) + 1, tick_notional)
    )
    asks = list(
        range(round(last_lob["ask_px1"] * hands), max_price_notional + 1, tick_notional)
    )
    between_ask_bid = list(range(bids[-1] + tick_notional, asks[0], tick_notional))
    prices_list = bids + between_ask_bid + asks
    price_levels = len(prices_list)

    # volume vector
    last_volume = {}
    last_volume[round(last_lob[f"bid_px1"] * hands)] = last_lob[f"bid_sz1"] + 10
    last_volume[round(last_lob[f"ask_px1"] * hands)] = last_lob[f"ask_sz1"] + 10
    for i in range(2, 6):
        last_volume[round(last_lob[f"bid_px{i}"] * hands)] = last_lob[f"bid_sz{i}"]
        last_volume[round(last_lob[f"ask_px{i}"] * hands)] = last_lob[f"ask_sz{i}"]
    prices_volume = []
    for px in prices_list:
        if px in last_volume.keys():
            prices_volume.append(last_volume[px])
        else:
            prices_volume.append(10000)

    # weights
    weights = np.zeros(price_levels)
    mid = price_levels / 2 - 0.5
    if avg_price > last_lob["ask_px1"]:
        mid += 0.5
    elif avg_price < last_lob["bid_px1"]:
        mid -= 0.5
    for i in range(price_levels):
        weights[i] = (i - mid) ** 2

    # optimize
    x = cp.Variable(price_levels, integer=True)
    a = np.array([prices_list, [1] * price_levels])
    b = np.array([trade_notional, trade_size])
    objective = cp.Minimize(
        cp.sum(cp.pos(x - prices_volume)) * 2.2
        + cp.sum(cp.pos(x))
        + cp.sum(cp.multiply(weights, x)) * 2
    )
    constriants = [0 <= x, a @ x == b]
    problem = cp.Problem(objective, constriants)
    problem.solve(solver=cp.CPLEX, verbose=False)
    if problem.status != "optimal":
        print("failed")
        return []

    # process results
    decomposed_vol = [round(v) for v in x.value]
    all_orders = []
    unknown_exec = []
    for px in bids:
        cur_vol = decomposed_vol.pop(0)
        if cur_vol > 0:
            all_orders.append({"side": "sell", "price": px / hands, "volume": cur_vol})
    for px in between_ask_bid:
        cur_vol = decomposed_vol.pop(0)
        if cur_vol > 0:
            order_px = px / hands
            if order_px <= cur_lob["bid_px1"]:
                direction = "buy"
            elif order_px >= cur_lob["ask_px1"]:
                direction = "sell"
            else:
                direction = "unknown"
            cur_record = {"side": direction, "price": order_px, "volume": cur_vol}
            if split_unknown and direction == "unknown":
                unknown_exec.append(cur_record)
            else:
                all_orders.append(cur_record)
    for px in asks:
        cur_vol = decomposed_vol.pop(0)
        if cur_vol > 0:
            all_orders.append({"side": "buy", "price": px / hands, "volume": cur_vol})

    # split unkown orders
    if split_unknown and unknown_exec:
        all_buy_volume = 0
        all_sell_volume = 0
        for ord in all_orders:
            if ord["side"] == "buy":
                all_buy_volume += ord["volume"]
            elif ord["side"] == "sell":
                all_sell_volume += ord["volume"]
        all_classified_volume = all_buy_volume + all_sell_volume
        all_unknown_volume = 0
        for ord in unknown_exec:
            all_unknown_volume += ord["volume"]
        if all_buy_volume + all_sell_volume > 0:
            buy_order_ratio = all_buy_volume / all_classified_volume
        else:
            buy_order_ratio = 0.5
        if all_unknown_volume <= all_classified_volume:
            assigned_buy_volume = round(all_unknown_volume * buy_order_ratio)
        else:
            assigned_buy_volume = (
                all_buy_volume
                + (all_unknown_volume - all_classified_volume) // 2
                + round(buy_order_ratio)
            )
        for exec in unknown_exec:
            cur_total = exec["volume"]
            cur_buy = min(cur_total, assigned_buy_volume)
            assigned_buy_volume -= cur_buy
            cur_sell = cur_total - cur_buy
            if cur_buy > 0:
                all_orders.append(
                    {"side": "buy", "price": exec["price"], "volume": cur_buy}
                )
            if cur_sell > 0:
                all_orders.append(
                    {"side": "sell", "price": exec["price"], "volume": cur_sell}
                )
        all_orders.sort(key=lambda x: x["price"])

    return all_orders


def recover_mo_core_lv2(
    last_lob, cur_lob, tick_size: float, hands: int, split_unknown: bool
) -> list:
    """
    仅使用一档价位猜成交
    """
    trade_notional = cur_lob["trade_notional"]
    trade_size = cur_lob["trade_sz"]
    if trade_size == 0:
        return []
    avg_price = trade_notional / trade_size / hands
    tick_notional = round(tick_size * hands)
    last_mid_px = (last_lob["bid_px1"] + last_lob["ask_px1"]) / 2
    if avg_price < last_mid_px:
        avg_price_boundary = (int(avg_price / tick_size) - 1) * tick_size
    else:
        avg_price_boundary = (int(avg_price / tick_size) + 2) * tick_size

    # price vector
    min_price = min(last_lob["bid_px1"], avg_price_boundary, cur_lob["bid_px1"])
    min_price_notional = round(min_price * hands)
    max_price = max(last_lob["ask_px1"], avg_price_boundary, cur_lob["ask_px1"])
    max_price_notional = round(max_price * hands)
    bids = list(
        range(min_price_notional, round(last_lob["bid_px1"] * hands) + 1, tick_notional)
    )
    asks = list(
        range(round(last_lob["ask_px1"] * hands), max_price_notional + 1, tick_notional)
    )
    between_ask_bid = list(range(bids[-1] + tick_notional, asks[0], tick_notional))
    prices_list = bids + between_ask_bid + asks
    price_levels = len(prices_list)

    # volume vector
    last_volume = {}
    last_volume[round(last_lob[f"bid_px1"] * hands)] = last_lob[f"bid_sz1"] + 10
    last_volume[round(last_lob[f"ask_px1"] * hands)] = last_lob[f"ask_sz1"] + 10
    prices_volume = []
    for px in prices_list:
        if px in last_volume.keys():
            prices_volume.append(last_volume[px])
        else:
            prices_volume.append(10000)

    # weights
    weights = np.zeros(price_levels)
    mid = price_levels / 2 - 0.5
    if avg_price > last_lob["ask_px1"]:
        mid += 0.5
    elif avg_price < last_lob["bid_px1"]:
        mid -= 0.5
    for i in range(price_levels):
        weights[i] = (i - mid) ** 2

    # optimize
    x = cp.Variable(price_levels, integer=True)
    a = np.array([prices_list, [1] * price_levels])
    b = np.array([trade_notional, trade_size])
    objective = cp.Minimize(
        cp.sum(cp.pos(x - prices_volume)) * 2.2
        + cp.sum(cp.pos(x))
        + cp.sum(cp.multiply(weights, x)) * 2
    )
    constriants = [0 <= x, a @ x == b]
    problem = cp.Problem(objective, constriants)
    problem.solve(solver=cp.CPLEX, verbose=False)
    if problem.status != "optimal":
        print("failed")
        return []

    # process results
    decomposed_vol = [round(v) for v in x.value]
    all_orders = []
    unknown_exec = []
    for px in bids:
        cur_vol = decomposed_vol.pop(0)
        if cur_vol > 0:
            all_orders.append({"side": "sell", "price": px / hands, "volume": cur_vol})
    for px in between_ask_bid:
        cur_vol = decomposed_vol.pop(0)
        if cur_vol > 0:
            order_px = px / hands
            if order_px <= cur_lob["bid_px1"]:
                direction = "buy"
            elif order_px >= cur_lob["ask_px1"]:
                direction = "sell"
            else:
                direction = "unknown"
            cur_record = {"side": direction, "price": order_px, "volume": cur_vol}
            if split_unknown and direction == "unknown":
                unknown_exec.append(cur_record)
            else:
                all_orders.append(cur_record)
    for px in asks:
        cur_vol = decomposed_vol.pop(0)
        if cur_vol > 0:
            all_orders.append({"side": "buy", "price": px / hands, "volume": cur_vol})

    # split unkown orders
    if split_unknown and unknown_exec:
        all_buy_volume = 0
        all_sell_volume = 0
        for ord in all_orders:
            if ord["side"] == "buy":
                all_buy_volume += ord["volume"]
            elif ord["side"] == "sell":
                all_sell_volume += ord["volume"]
        all_classified_volume = all_buy_volume + all_sell_volume
        all_unknown_volume = 0
        for ord in unknown_exec:
            all_unknown_volume += ord["volume"]
        if all_buy_volume + all_sell_volume > 0:
            buy_order_ratio = all_buy_volume / all_classified_volume
        else:
            buy_order_ratio = 0.5
        if all_unknown_volume <= all_classified_volume:
            assigned_buy_volume = round(all_unknown_volume * buy_order_ratio)
        else:
            assigned_buy_volume = (
                all_buy_volume
                + (all_unknown_volume - all_classified_volume) // 2
                + round(buy_order_ratio)
            )
        for exec in unknown_exec:
            cur_total = exec["volume"]
            cur_buy = min(cur_total, assigned_buy_volume)
            assigned_buy_volume -= cur_buy
            cur_sell = cur_total - cur_buy
            if cur_buy > 0:
                all_orders.append(
                    {"side": "buy", "price": exec["price"], "volume": cur_buy}
                )
            if cur_sell > 0:
                all_orders.append(
                    {"side": "sell", "price": exec["price"], "volume": cur_sell}
                )
        all_orders.sort(key=lambda x: x["price"])

    return all_orders


class MosRecoverIC(IndexCalculator):
    def __init__(self, tick_size: float = 0.005, hands: int = 10000, sym: str = None):
        super().__init__(1)
        self.last_lob = None
        if sym is None:
            self.tick_size = tick_size
            self.hands = hands
        else:
            info = get_instrument_info(sym)
            self.tick_size = info["tick_size"]
            self.hands = info["hands"]

    def calculate(self, new_data):
        if self.last_lob is None:
            self.result = []
        else:
            if self.last_lob.name.hour < 12 and new_data.name.hour > 12:
                try:
                    self.result = recover_mo_core_lv2(
                        self.last_lob, new_data, self.tick_size, self.hands, True
                    )
                except:
                    self.result = []
            else:
                self.result = recover_mo_core_lv2(
                    self.last_lob, new_data, self.tick_size, self.hands, True
                )
        self.last_lob = new_data
