"""Pickle 实现的 ResultDB"""

import datetime
import os
from typing import List, Optional, Union

import pandas as pd

from .result_db import ResultDB


class PklResultDB(ResultDB):
    """
    由于PEU的运算通常极为缓慢，因此需要缓存前期计算好的数据用于后续研究。
    ResultDB负责管理已有结果，所有数据以"sym_date.pkl"的形式存放，datetime.da
    """

    def __init__(self, db_directory):
        if os.path.exists(db_directory):
            self.db_directory = db_directory
        else:
            raise FileNotFoundError(f"{db_directory} not found.")

    def get_existed_columns(self, sym: str, date: datetime.date) -> list:
        path = self._get_path(sym, date)
        if os.path.exists(path):
            data = pd.read_pickle(path, compression="gzip")
            return list(data.columns)
        return []

    def save_data(self, sym, date, new_data) -> None:
        path = self._get_path(sym, date)
        if os.path.exists(path):
            ori_data = pd.read_pickle(path, compression="gzip")
            merged_data = ori_data.merge(
                new_data,
                left_index=True,
                right_index=True,
                how="outer",
                suffixes=("_x", ""),
            )
            merged_data = merged_data.loc[:, ~merged_data.columns.str.endswith("_x")]
            merged_data.to_pickle(path, compression="gzip")
        else:
            new_data.to_pickle(path, compression="gzip")
        return None

    def get_data(
        self,
        sym: str,
        date: datetime.date,
        factors: Optional[Union[List[str], str]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        获取指定股票和日期的数据

        Args:
            sym: 股票代码
            date: 日期
            factors: 可选的因子列表或单个因子名，用于筛选返回的列

        Returns:
            包含数据的 DataFrame，如果不存在的返回 None
        """
        path = self._get_path(sym, date)
        if os.path.exists(path):
            data = pd.read_pickle(path, compression="gzip")
            if factors is not None:
                if isinstance(factors, str):
                    factors = [factors]
                # 只返回请求的因子列
                existing_factors = [f for f in factors if f in data.columns]
                if existing_factors:
                    return data[existing_factors]
                return None
            return data
        return None

    def _get_path(self, sym: str, date: datetime.date) -> pd.DataFrame:
        path = os.path.join(self.db_directory, f"{sym}_{str(date)}.pkl")
        return path


# 向后兼容别名
ResultDB = PklResultDB
