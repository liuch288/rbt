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
        # STEP 1: 获取已有因子列表（轻量级检查）
        cur_sym = self.md_engine.cur_sym
        cur_date = self.md_engine.cur_date
        existed_factors = self.result_db.get_existing_factors(cur_sym, cur_date)

        # STEP 2: 加入需要计算的DMU
        # 用户DMU
        new_dmus = []
        for dmu in self.dmus:
            if not any(col.startswith(dmu.name) for col in existed_factors):
                new_dmus.append(dmu)
            elif dmu.name in self.recalculate_dmu_names:
                new_dmus.append(dmu)
        # 后置平台DMU
        new_dmus.append(self.position_pnl_dmu_class())

        # STEP 3: 加入需要计算的PEU
        new_peus = []
        for peu in self.peus:
            if not any(col.startswith(peu.name) for col in existed_factors):
                new_peus.append(peu)
            elif peu.name in self.recalculate_peu_names:
                new_peus.append(peu)

        # STEP 4: 查询各 unit 依赖的因子，去重后加载
        required_factors = set()
        for dmu in new_dmus:
            required_factors.update(dmu.dependencies())
        for peu in new_peus:
            required_factors.update(peu.dependencies())

        if required_factors:
            loaded_data = self.result_db.get_data(cur_sym, cur_date, factors=list(required_factors))
        else:
            loaded_data = pd.DataFrame()
        if loaded_data is None:
            loaded_data = pd.DataFrame()

        # STEP 4.5: 检查所有 unit 的依赖是否已在 loaded_data 中
        for unit in list(new_dmus) + list(new_peus):
            missing = [
                f for f in unit.dependencies()
                if not any(col.startswith(f) for col in loaded_data.columns)
            ]
            if missing:
                raise RuntimeError(
                    f"Unit '{unit.name}' depends on {missing}, "
                    f"but they are not found in ResultDB. "
                    f"Please run the corresponding units first and save results."
                )

        # STEP 5: 执行运算
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
            if cur_time in loaded_data.index:
                unit_results = loaded_data.loc[cur_time].to_dict()
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
                # 将依赖的 unit 结果拼接到 future_md 中
                if peu.dependencies():
                    future_unit_results = loaded_data.loc[
                        loaded_data.index.isin(future_md.index)
                    ]
                    future_md = pd.concat([future_md, future_unit_results], axis=1)
                result = peu.estimate(future_md)
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

        # STEP 6: 保存结果
        new_data = pd.DataFrame.from_dict(self.unit_results, orient="index")
        self.result_db.save_data(cur_sym, cur_date, new_data, skip_existing=True)
