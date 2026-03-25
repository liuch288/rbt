"""FactorStore 实现的 ResultDB"""

import datetime
from typing import List, Optional, Union

import pandas as pd

from factorstore import FactorStore

from .result_db import ResultDB


class FsResultDB(ResultDB):
    """
    基于 FactorStore 的 ResultDB 实现。
    使用 Parquet 文件存储因子数据，支持多频率因子管理。
    """

    def __init__(self, root_path: str = None, frequency: str = "tick"):
        """
        初始化 FsResultDB。

        Args:
            root_path: FactorStore 根目录路径
            frequency: 数据频率，默认 "tick"
        """
        self.store = FactorStore(root_path=root_path)
        self.frequency = frequency

    def _get_trade_date(self, date: datetime.date) -> str:
        """将 datetime.date 转换为字符串格式 YYYY-MM-DD"""
        return date.strftime("%Y-%m-%d")

    def get_existing_factors(self, sym: str, date: datetime.date) -> List[str]:
        """
        获取指定股票和日期已存在的列（因子名列表）。

        Args:
            sym: 股票代码
            date: 日期

        Returns:
            因子名列表
        """
        trade_date = self._get_trade_date(date)
        return self.store.list_factors(
            contract=sym,
            trade_date=trade_date,
            frequency=self.frequency,
        )

    def save_data(
        self, sym: str, date: datetime.date, new_data: pd.DataFrame,
        skip_existing: bool = False,
    ) -> None:
        """
        保存数据到数据库。

        输入 DataFrame 的 index 应为时间戳，列名格式：{factor_name}__{indicator}
        - ts 不能作为普通列，只能在 index 中
        - 解析因子名：取 __ 前缀部分
        - 用 list_factors 检查已存在因子
        - FactorStore 自动处理 index 转换，列名原样保存

        Args:
            sym: 股票代码
            date: 日期
            new_data: 要保存的 DataFrame
            skip_existing: 若为 True，已存在的因子跳过；
                           若为 False（默认），遇到重复则抛出 ValueError
        """
        trade_date = self._get_trade_date(date)

        # ts 不应作为普通列存在，应在 index 中
        if "ts" in new_data.columns:
            raise ValueError(
                "'ts' 不应作为列存在，应作为 DataFrame 的 index。"
            )

        # 解析列名，提取因子名
        factor_names = set()
        for col in new_data.columns:
            if "__" not in col:
                raise ValueError(
                    f"列名 '{col}' 不符合格式要求，应为 {{factor_name}}__{{indicator}}"
                )
            factor_name = col.split("__")[0]
            factor_names.add(factor_name)

        # 检查已存在的因子
        existing_factors = set(
            self.store.list_factors(
                contract=sym,
                trade_date=trade_date,
                frequency=self.frequency,
            )
        )

        # 检查冲突
        conflicts = factor_names & existing_factors
        if conflicts:
            if not skip_existing:
                raise ValueError(
                    f"因子 {conflicts} 已存在，无法覆盖。如需更新，请先删除再保存。"
                )
            print(f"跳过已存在的因子: {conflicts}")

        # 保存每个因子（FactorStore 会自动处理 index -> ts）
        for factor_name in factor_names:
            if factor_name in existing_factors:
                continue

            factor_cols = [col for col in new_data.columns if col.startswith(f"{factor_name}__")]
            factor_df = new_data[factor_cols]

            self.store.save_factor(
                contract=sym,
                trade_date=trade_date,
                factor_name=factor_name,
                df=factor_df,
                frequency=self.frequency,
            )

    def get_data(
        self,
        sym: str,
        date: datetime.date,
        factors: Optional[Union[List[str], str]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        获取指定股票和日期的数据。

        Args:
            sym: 股票代码
            date: 日期
            factors: 可选的因子列表或单个因子名，用于筛选返回的列

        Returns:
            包含数据的 DataFrame，如果不存在的返回 None
        """
        trade_date = self._get_trade_date(date)

        # 获取所有因子名
        all_factors = self.store.list_factors(
            contract=sym,
            trade_date=trade_date,
            frequency=self.frequency,
        )

        if not all_factors:
            return None

        # 如果没有指定因子，返回所有
        if factors is None:
            factors_to_load = all_factors
        else:
            if isinstance(factors, str):
                factors = [factors]
            # 前缀匹配筛选（与 PklResultDB 一致）
            factors_to_load = [f for f in all_factors if any(f.startswith(factor) for factor in factors)]

        if not factors_to_load:
            return None

        # 加载匹配的因子
        try:
            data = self.store.load_factors(
                contract=sym,
                trade_date=trade_date,
                factor_names=factors_to_load,
                frequency=self.frequency,
            )

            return data
        except FileNotFoundError:
            return None
