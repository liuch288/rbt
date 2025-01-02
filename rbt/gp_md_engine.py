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
