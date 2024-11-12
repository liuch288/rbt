import pandas as pd

from .pnl_estimate_unit import PnlEstimateUnit


class BisideQuoteMosPEU(PnlEstimateUnit):
    def __init__(
        self,
        watching_time: float = None,
        watching_mds: int = None,
        lb: int = 1,
        la: int = 1,
        tick_size: float = 0.005,
        name: str = None,
    ):
        super().__init__(watching_time, watching_mds, name)
        self.lb = lb
        self.la = la
        self.tick_size = tick_size
        self.digits = len(str(tick_size).split(".")[1])

    def estimate(self, future_data, *args, **kwargs) -> dict:
        init_md = future_data.iloc[0]
        buy_order_price = round(
            init_md["bid_px1"] - (self.lb - 1) * self.tick_size, self.digits
        )
        sell_order_price = round(
            init_md["ask_px1"] + (self.la - 1) * self.tick_size, self.digits
        )

        # -------------------------------------------
        df = future_data["exec_after"].reset_index()
        df_expanded = df.explode("exec_after").dropna()

        # 将exec_after中的字典元素展开为列
        df_expanded = pd.concat(
            [
                df_expanded.drop(["exec_after"], axis=1),
                df_expanded["exec_after"].apply(pd.Series),
            ],
            axis=1,
        )
        df_expanded
        # -------------------------------------------

        buy_order_hits = future_data[future_data["ask_px1"] <= buy_order_price]
        buy_order_executed = len(buy_order_hits) > 0

        sell_order_hits = future_data[future_data["bid_px1"] >= sell_order_price]
        sell_order_executed = len(sell_order_hits) > 0

        pnl = 0.0
        if (buy_order_executed == True) & (sell_order_executed == False):
            pnl = future_data.iloc[-1]["bid_px1"] - buy_order_price
        if (buy_order_executed == False) & (sell_order_executed == True):
            pnl = sell_order_price - future_data.iloc[-1]["ask_px1"]
        if (buy_order_executed == True) & (sell_order_executed == True):
            pnl = sell_order_price - buy_order_price

        cur_result = {
            "pnl": pnl,
            "buy_order_executed": buy_order_executed,
            "sell_order_executed": sell_order_executed,
        }
        return cur_result
