import pandas as pd
from progressbar import Bar, ETA, Timer, Percentage, ProgressBar

from .md import MdEngine
from .dmu import DecisionMakingUnit, PositionPnlDMU
from .peu import PnlEstimateUnit
from .result_db import ResultDB


class Strategy(object):
    def __init__(self) -> None:
        self.dmus = []
        self.recalculate_dmu_names = []
        self.peus = []
        self.recalculate_peu_names = []

    def register_dmu(self, dmu: DecisionMakingUnit, recalculate:bool=False):
        if recalculate:
            self.recalculate_dmu_names.append(dmu.name)
        self.dmus.append(dmu)

    def register_peu(self, peu: PnlEstimateUnit, recalculate:bool=False):
        if recalculate:
            self.recalculate_peu_names.append(peu.name)
        self.peus.append(peu)

    def register_md_engine(self, md_engine: MdEngine):
        self.md_engine = md_engine

    def register_result_db(self, result_db: ResultDB):
        self.result_db = result_db

    def run(self, show_progress: bool = False):
        # STEP 1: 加入需要计算的DMU
        # 用户DMU
        cur_sym = self.md_engine.cur_sym
        cur_date = self.md_engine.cur_date
        existed_cols = self.result_db.get_existed_columns(cur_sym, cur_date)
        new_dmus = []
        for dmu in self.dmus:
            if not any(col.startswith(dmu.name) for col in existed_cols):
                new_dmus.append(dmu)
        # 后置平台DMU
        new_dmus.append(PositionPnlDMU())

        # STEP 2: 加入需要计算的PEU
        new_peus = []
        for peu in self.peus:
            if not any(col.startswith(peu.name) for col in existed_cols):
                new_peus.append(peu)

        # STEP 3: 执行运算
        self.unit_results = {}
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
            for dmu in new_dmus:
                dmu_name = dmu.name
                result = dmu.on_market_data(new_md, unit_results)
                for key in result.keys():
                    unit_results[f"{dmu_name}_{key}"] = result[key]

            for peu in new_peus:
                peu_name = peu.name
                future_md = self.md_engine.get_future_md(
                    peu.watching_time, peu.watching_mds
                )
                result = peu.estimate(future_md, unit_results)
                for key in result.keys():
                    unit_results[f"{peu_name}_{key}"] = result[key]
            self.unit_results[cur_time] = unit_results

            if not self.md_engine.finish_current_md():
                break

            if show_progress:
                step_count += 1
                bar.update(step_count)       

        if show_progress:
            bar.finish()
        
        # STEP 4: 保存结果
        new_data = pd.DataFrame.from_dict(self.unit_results, orient="index")
        self.result_db.save_data(cur_sym, cur_date, new_data)
