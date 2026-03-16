import pandas as pd
from progressbar import Bar, ETA, Timer, Percentage, ProgressBar

from .md import MdEngine
from .dmu import DecisionMakingUnit, PositionPnlDMU
from .peu import PnlEstimateUnit
from .result_db import ResultDB
from .util import get_instrument_info


class Strategy(object):
    def __init__(self, position_pnl_dmu_class=PositionPnlDMU) -> None:
        self.dmus = []
        self.recalculate_dmu_names = []
        self.peus = []
        self.recalculate_peu_names = []
        self.position_pnl_dmu_class = position_pnl_dmu_class
        self.contract_info = None

    def set_contract_info(self, symbol: str, tick_size: float = None, hands: int = None, digits: int = None):
        """提前设置合约信息，后续注册的 unit 会自动获取"""
        self.contract_info = {
            "symbol": symbol,
            "tick_size": tick_size,
            "hands": hands,
            "digits": digits,
        }

    def register_dmu(self, dmu: DecisionMakingUnit, recalculate: bool = False):
        if recalculate:
            self.recalculate_dmu_names.append(dmu.name)
        self.dmus.append(dmu)
        if self.contract_info:
            dmu.register_contract_info(**self.contract_info)

    def register_peu(self, peu: PnlEstimateUnit, recalculate: bool = False):
        if recalculate:
            self.recalculate_peu_names.append(peu.name)
        self.peus.append(peu)
        if self.contract_info:
            peu.register_contract_info(**self.contract_info)

    def register_md_engine(self, md_engine: MdEngine):
        self.md_engine = md_engine
        if self.contract_info is None and md_engine.cur_sym:
            info = get_instrument_info(md_engine.cur_sym)
            if info:
                self.set_contract_info(
                    symbol=md_engine.cur_sym,
                    tick_size=info.get("tick_size"),
                    hands=info.get("hands"),
                    digits=info.get("digits"),
                )

    def register_result_db(self, result_db: ResultDB):
        self.result_db = result_db

    def run(self, show_progress: bool = False, bgm: dict = None):
        # STEP 1: 读入已有数据
        cur_sym = self.md_engine.cur_sym
        cur_date = self.md_engine.cur_date
        existed_data = self.result_db.get_data(cur_sym, cur_date)
        if existed_data is None:
            existed_data = pd.DataFrame()
        existed_cols = existed_data.columns

        # STEP 2: 加入需要计算的DMU
        # 用户DMU
        new_dmus = []
        for dmu in self.dmus:
            if not any(col.startswith(dmu.name) for col in existed_cols):
                new_dmus.append(dmu)
            elif dmu.name in self.recalculate_dmu_names:
                new_dmus.append(dmu)
        # 后置平台DMU
        new_dmus.append(self.position_pnl_dmu_class())

        # STEP 3: 加入需要计算的PEU
        new_peus = []
        for peu in self.peus:
            if not any(col.startswith(peu.name) for col in existed_cols):
                new_peus.append(peu)
            elif peu.name in self.recalculate_peu_names:
                new_peus.append(peu)

        # STEP 4: 执行运算
        self.unit_results = {}
        if bgm is None:
            bgm = {}
        if show_progress:
            widgets = ["Testing:", Percentage(), " ", Bar(), " ", ETA(), ", ", Timer()]
            bar = ProgressBar(maxval=len(self.md_engine.raw_md), widgets=widgets)
            bar.start()
            step_count = 0
        while True:
            new_md = self.md_engine.get_current_md()
            if new_md is None:
                break
            cur_time = new_md.name

            unit_results = {}
            if cur_time in existed_data.index:
                unit_results = existed_data.loc[cur_time].to_dict()
            unit_results.update(bgm)
            for dmu in new_dmus:
                dmu_name = dmu.name
                result = dmu.on_market_data(new_md, unit_results)
                for key in result.keys():
                    unit_results[f"{dmu_name}__{key}"] = result[key]

            for peu in new_peus:
                peu_name = peu.name
                future_md = self.md_engine.get_future_md(
                    peu.watching_time, peu.watching_mds
                )
                result = peu.estimate(future_md, unit_results)
                for key in result.keys():
                    unit_results[f"{peu_name}__{key}"] = result[key]
            self.unit_results[cur_time] = unit_results

            if not self.md_engine.finish_current_md():
                break

            if show_progress:
                step_count += 1
                bar.update(step_count)

        if show_progress:
            bar.finish()

        # STEP 5: 保存结果
        new_data = pd.DataFrame.from_dict(self.unit_results, orient="index")
        self.result_db.save_data(cur_sym, cur_date, new_data)
