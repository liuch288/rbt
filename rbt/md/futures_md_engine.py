import datetime
import sys
from pathlib import Path

import pandas as pd

from rbt.md import MdEngine
from futures_db import FuturesDB
from futures_db.config import CompressionType, DEFAULT_COMPRESSION, DEFAULT_DATA_PATH


class FuturesMdEngine(MdEngine):
    def __init__(
        self,
        base_path: str = DEFAULT_DATA_PATH,
        compression: CompressionType = DEFAULT_COMPRESSION,
    ) -> None:
        """
        Args:
            base_path: FuturesDB 数据存储根目录，默认从环境变量 FUTURESDB_PATH 读取
            compression: 压缩类型，支持 'gzip', 'bz2', 'zip', 'xz', 'zstd'，默认 'gzip'
        """
        super().__init__()
        self.futures_db = FuturesDB(base_path=base_path, compression=compression)

    def prepare_data(self, sym: str, date: datetime.date):
        df = self.futures_db.get_tick(sym, date)

        md = df[
            [
                "sym",
                "bid_px1",
                "ask_px1",
                "bid_sz1",
                "ask_sz1",
                "last_px",
                "tot_sz",
                "tot_notional",
                "oi",
                "upper_limit",
                "lower_limit",
            ]
        ].copy()

        # 计算增量（每tick的成交）
        md["trade_notional"] = md["tot_notional"].diff()
        md["trade_sz"] = md["tot_sz"].diff()

        # 第一行没有增量，设为0
        md["trade_notional"] = md["trade_notional"].fillna(0)
        md["trade_sz"] = md["trade_sz"].fillna(0)

        if not isinstance(md.index, pd.DatetimeIndex):
            raise ValueError("FuturesDB tick data must have DatetimeIndex")

        self._register_raw_md(sym, date, md)
