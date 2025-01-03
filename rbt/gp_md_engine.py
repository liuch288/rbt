import datetime
import os

import pandas as pd

from .md_engine import MdEngine


class GpMdEngine(MdEngine):
    def __init__(self, db_path: str) -> None:
        super().__init__()
        self.db_path = db_path

    def prepare_data(self, sym: str, date: datetime.date):
        self.tick_size = self.get_tick_size(sym)
        data_path = os.path.join(self.db_path, f"gp_tick_{sym}_{str(date)}.csv")
        md = pd.read_csv(data_path)

        # 将 datetime 列转换为 pd.DatetimeIndex
        md["datetime"] = pd.to_datetime(md["datetime"], format="%Y%m%d%H%M%S")
        md.set_index("datetime", inplace=True)

        # 调用 _register_raw_md 方法注册处理好的数据
        self._register_raw_md(sym, date, md, recover_mo=False)

    def get_tick_size(self, code):
        if code.startswith("sh"):
            num_part = code[2:]
            if num_part.startswith("6"):
                return 0.01
            else:
                return 0.001
        elif code.startswith("sz"):
            num_part = code[2:]
            if num_part.startswith(("00", "30")):
                return 0.01
            else:
                return 0.001
        return 0.01
