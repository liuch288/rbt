"""ResultDB 抽象基类定义"""

import abc
import datetime
from typing import List, Optional, Union

import pandas as pd


class ResultDB(abc.ABC):
    """
    由于PEU的运算通常极为缓慢，因此需要缓存前期计算好的数据用于后续研究。
    ResultDB负责管理已有结果，所有数据以"sym_date.pkl"的形式存放。
    """

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def get_existing_factors(self, sym: str, date: datetime.date) -> List[str]:
        """
        获取指定股票和日期已存在的列

        Args:
            sym: 股票代码
            date: 日期

        Returns:
            列名列表
        """
        pass

    @abc.abstractmethod
    def save_data(
        self,
        sym: str,
        date: datetime.date,
        new_data: pd.DataFrame,
        skip_existing: bool = False,
    ) -> None:
        """
        保存数据到数据库

        Args:
            sym: 股票代码
            date: 日期
            new_data: 要保存的 DataFrame
            skip_existing: 若为 True，已存在的因子跳过；若为 False（默认），遇到重复则抛出 ValueError
        """
        pass
