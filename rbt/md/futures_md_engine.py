import datetime
import sys
from pathlib import Path

import pandas as pd

from rbt.md import MdEngine
from futures_db import FuturesDB


class FuturesMdEngine(MdEngine):
    def __init__(self, futures_db: FuturesDB, recover_mo: bool = True) -> None:
        super().__init__()
        self.futures_db = futures_db
        self.recover_mo = recover_mo

    def prepare_data(self, sym: str, date: datetime.date):
        df = self.futures_db.get_tick(sym, date)
        
        md = df[["sym", "bid_px1", "ask_px1", "bid_sz1", "ask_sz1", "last_px", "tot_sz", "tot_notional", "oi",  "upper_limit",  "lower_limit"]].copy()
        
        # 计算增量（每tick的成交）
        md["trade_notional"] = md["tot_notional"].diff()
        md["trade_sz"] = md["tot_sz"].diff()
        
        # 第一行没有增量，设为0
        md["trade_notional"] = md["trade_notional"].fillna(0)
        md["trade_sz"] = md["trade_sz"].fillna(0)
        
        if not isinstance(md.index, pd.DatetimeIndex):
            raise ValueError("FuturesDB tick data must have DatetimeIndex")
        
        if self.recover_mo:
            # 使用 lv1 模式的 MosRecoverIC（仅需 L1 数据）
            from rbt.ic import MosRecoverIC
            recover_ic = MosRecoverIC(sym=sym, md_type="lv1")
            all_exec = []
            for _, row in md.iterrows():
                exec_result = recover_ic.update(row)
                all_exec.append(exec_result)
            md["exec_before"] = all_exec
            all_exec.append([])
            md["exec_after"] = all_exec[1:]
        
        self._register_raw_md(sym, date, md, recover_mo=False)
