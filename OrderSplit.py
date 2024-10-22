import datetime

import cvxpy
import matplotlib.pyplot as plt
import numpy as np


def recover_mos(
    lob, trade_amount: int, trade_size: int, split_unknown: bool = False
) -> list:
    """Recover market orders

    Args:
        lob (Any): a row of a DataFrame records the lob status at t-1
        trade_amount (int): the trade notional from t-1 to t
        trade_size (int): the trade size from t-1 to t
        split_unknown (bool):

    Returns:
        list: a list of dictionary
    """
    bids = [round(lob["bid_px2"] * 10000), round(lob["bid_px1"] * 10000)]
    asks = [round(lob["ask_px1"] * 10000), round(lob["ask_px2"] * 10000)]
    between_ask_bid = list(range(bids[-1] + 50, asks[0], 50))
    prices_list = bids + between_ask_bid + asks

    price_levels = len(prices_list)
    x = cvxpy.Variable(price_levels, integer=True)

    a = np.array([prices_list, [1] * price_levels])
    b = np.array([trade_amount, trade_size])

    objective = cvxpy.Minimize(x[0] + x[-1])
    constriants = [0 <= x, a @ x == b]
    problem = cvxpy.Problem(objective, constriants)
    results = problem.solve(solver=cvxpy.CPLEX, verbose=False)

    if (problem.status != "optimal") or (results > trade_size / 2):
        return None

    sell_orders = [round(val) for val in x.value[:2]]
    buy_orders = [round(val) for val in x.value[-2:]]
    unknown_orders = [round(val) for val in x.value[2:-2]]

    all_orders = []
    if sell_orders[0]:
        all_orders.append(
            {
                "side": "sell",
                "price": bids[0] / 10000,
                "volume": sell_orders[0],
                "position": "bid2",
            }
        )
    if sell_orders[1]:
        all_orders.append(
            {
                "side": "sell",
                "price": bids[1] / 10000,
                "volume": sell_orders[1],
                "position": "bid1",
            }
        )

    if split_unknown:
        all_buy_volume = sum(buy_orders)
        all_sell_volume = sum(sell_orders)
        if all_buy_volume + all_sell_volume > 0:
            buy_order_ratio = all_buy_volume / (all_buy_volume + all_sell_volume)
        else:
            buy_order_ratio = 0.5
        for i in range(len(between_ask_bid)):
            cur_price = between_ask_bid[i]
            cur_unknown_volume = unknown_orders[i]
            buy_unknown_volume = round(cur_unknown_volume * buy_order_ratio)
            sell_unknown_volume = cur_unknown_volume - buy_unknown_volume
            if buy_unknown_volume:
                all_orders.append(
                    {
                        "side": "buy",
                        "price": cur_price / 10000,
                        "volume": buy_unknown_volume,
                        "position": "mid",
                    }
                )
            if sell_unknown_volume:
                all_orders.append(
                    {
                        "side": "sell",
                        "price": cur_price / 10000,
                        "volume": sell_unknown_volume,
                        "position": "mid",
                    }
                )
    else:
        for i in range(len(between_ask_bid)):
            all_orders.append(
                {
                    "side": "unknown",
                    "price": between_ask_bid[i] / 10000,
                    "volume": unknown_orders[i],
                    "position": "mid",
                }
            )

    if buy_orders[-2]:
        all_orders.append(
            {
                "side": "buy",
                "price": asks[-2] / 10000,
                "volume": buy_orders[-2],
                "position": "ask1",
            }
        )
    if buy_orders[-1]:
        all_orders.append(
            {
                "side": "buy",
                "price": asks[-1] / 10000,
                "volume": buy_orders[-1],
                "position": "ask2",
            }
        )

    return all_orders


class OrderSplit:
    def __init__(self) -> None:
        self.last_md = None

    def update(self, data) -> list:
        if self.last_md is None:
            self.last_md = data
            return []
        
        
        

        

