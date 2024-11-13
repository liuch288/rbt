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