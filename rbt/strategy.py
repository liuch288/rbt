from progressbar import Bar, ETA, Timer, Percentage, ProgressBar

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

    def run(self, show_progress: bool = False):
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
            for dmu in self.dmus:
                dmu_name = dmu.name
                result = dmu.on_market_data(new_md, unit_results)
                for key in result.keys():
                    unit_results[f"{dmu_name}_{key}"] = result[key]

            for peu in self.peus:
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
