from progressbar import ProgressBar

from .md_engine import MdEngine
from .dmu import DecisionMakingUnit
from .peu import PnlEstimateUnit


class Strategy(object):
    def __init__(self) -> None:
        self.dmus = []
        self.peus = []
        self.md_engine = None

    def register_dmu(self, dmu: DecisionMakingUnit):
        self.dmus.append(dmu)

    def register_peu(self, peu: PnlEstimateUnit):
        self.peus.append(peu)

    def register_md_engine(self, md_engine: MdEngine):
        self.md_engine = md_engine

    def run(self, show_progress:bool=False):
        self.dmu_results = {}
        self.pnl_estimations = {}
        if show_progress:
            bar = ProgressBar(maxval=len(self.md_engine.raw_md))
            bar.start()
            step_count = 0
        while True:
            new_md = self.md_engine.get_current_md()
            if new_md is None:
                break
            cur_time = new_md.name

            cur_dmu_results = {}
            for dmu in self.dmus:
                dmu_name = dmu.name
                result = dmu.on_market_data(new_md)
                for key in result.keys():
                    cur_dmu_results[f"{dmu_name}_{key}"] = result[key]
            self.dmu_results[cur_time] = cur_dmu_results

            cur_peu_results = {}
            for peu in self.peus:
                peu_name = peu.name
                future_md = self.md_engine.get_future_md(
                    peu.watching_time, peu.watching_mds
                )
                result = peu.estimate(future_md)
                for key in result.keys():
                    cur_peu_results[f"{peu_name}_{key}"] = result[key]
            self.pnl_estimations[cur_time] = cur_peu_results
            if not self.md_engine.finish_current_md():
                break
            
            if show_progress:
                step_count += 1
                bar.update(step_count)
        if show_progress:
            bar.finish()
