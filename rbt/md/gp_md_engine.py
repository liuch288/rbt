import datetime
import os

import pandas as pd

from .md_engine import MdEngine


class GpMdEngine(MdEngine):
    def __init__(self, db_path: str) -> None:
        super().__init__()
        self.db_path = db_path

    def prepare_data(self, sym: str, date: datetime.date):
        data_path = os.path.join(self.db_path, f"gp_tick_{sym}_{str(date)}.csv")
        md = pd.read_csv(data_path)

        # 将 datetime 列转换为 pd.DatetimeIndex
        md["datetime"] = pd.to_datetime(md["datetime"], format="%Y%m%d%H%M%S")
        md.set_index("datetime", inplace=True)

        # 计算每个行情戳的成交情况
        md["trade_sz"] = md["tot_sz"] - md["tot_sz"].shift()
        md["trade_notional"] = md["tot_notional"] - md["tot_notional"].shift()
        md = md.dropna(subset=["trade_sz", "trade_notional"], axis=0)

        # 调用 _register_raw_md 方法注册处理好的数据
        self._register_raw_md(sym, date, md, recover_mo=False)
