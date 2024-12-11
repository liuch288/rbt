import datetime
import os

import pandas as pd


class ResultDB(object):
    """
    由于PEU的运算通常极为缓慢，因此需要缓存前期计算好的数据用于后续研究。
    ResultDB负责管理已有结果，所有数据以“sym_date.pkl”的形式存放，datetime.da
    """

    def __init__(self, db_directory):
        if os.path.exists(db_directory):
            self.db_directory = db_directory
        else:
            raise FileNotFoundError(f"{db_directory} not found.")

    def query_existed_columns(self, sym: str, date: datetime.date) -> list:
        path = self._get_path(sym, date)
        data = pd.read_pickle(path, compression="gzip")
        return list(data.columns)

    def save_data(self, sym, date, new_data) -> None:
        return None

    def _get_path(self, sym: str, date: datetime.date) -> pd.DataFrame:
        path = os.path.join(self.db_directory, f"{sym}_{str(date)}.pkl")
        return path
