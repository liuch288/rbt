import pandas as pd

from .dmu import DecisionMakingUnit


class RealtimeStrategy(object):
    def __init__(self) -> None:
        self.dmus = []

    def register_dmu(self, dmu: DecisionMakingUnit):
        self.dmus.append(dmu)

    def run_once(self, new_md: pd.Series, bgm: dict = None) -> dict:
        """Process single realtime market data tick

        Args:
            new_md: Current market data as pandas Series
            bgm: Backtest global parameters (optional)

        Returns:
            dict: Combined results from all DMUs
        """
        unit_results = {}
        if bgm:
            unit_results.update(bgm)

        for dmu in self.dmus:
            result = dmu.on_market_data(new_md, unit_results)
            for key in result.keys():
                unit_results[f"{dmu.name}__{key}"] = result[key]

        return unit_results

    def on_end_of_day(self):
        """日终处理，遍历所有 DMU 执行日终逻辑"""
        for dmu in self.dmus:
            dmu.on_end_of_day()
