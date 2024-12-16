import datetime
import pandas as pd

from .ic import MosRecoverIC
from .util import get_instrument_info


class MdEngine(object):
    """
    用户继承MdEngine类，修改构造函数和prepare_data函数。
    在prepare_data函数中，用户需要将数据读取出来，改变列名为特定格式（必须包含sym、bid_px等列），并以Timestamp作为index。
    在prepare_data完成后，要出发_register_raw_md函数来保存处理好的数据表。
    原始数据表raw_md中需要恢复出行情戳之前和之后的市价单，分别命名为exec_before和exec_after,
    如果数据表中不包含exec_after列，将自动进行市价单拆分工作。
    """

    def __init__(self) -> None:
        self.cur_sym = None
        self.cur_date = None
        self.raw_md = None
        self.current_index = 0

    def prepare_data(self, sym: str, date: datetime.date):
        raise NotImplementedError("Subclasses should implement this method.")

    def _register_raw_md(self, sym: str, date: datetime.date, raw_md):
        """注册原始行情数据
        注意，sym必须是绝对代码，比如TS2503，而不能是TS01这种代号
        """
        if not isinstance(raw_md.index, pd.DatetimeIndex):
            raise ValueError("raw_md must be indexed by datetime.")
        self.cur_sym = sym
        self.cur_date = date
        self.raw_md = raw_md.sort_index().copy()
        self.current_index = 0
        if "exec_after" not in self.raw_md.columns:
            self.__recover_mo()

    def __recover_mo(self):
        all_exec = []
        sym = self.raw_md.iloc[0]["sym"]
        recover_mo_ic = MosRecoverIC(sym=sym)
        for _, cur_md in self.raw_md.iterrows():
            cur_mo = recover_mo_ic.update(cur_md)
            all_exec.append(cur_mo)
        self.raw_md["exec_before"] = all_exec
        all_exec.append([])
        self.raw_md["exec_after"] = all_exec[1:]

    def get_current_md(self):
        return self.raw_md.iloc[self.current_index]

    def get_future_md(self, period: float = None, mds: int = None) -> pd.DataFrame:
        if period is not None and mds is not None:
            raise ValueError("Only one of 'period' or 'mds' can be provided.")
        if period is not None:
            cur_time = self.raw_md.iloc[self.current_index].name
            end_time = cur_time + pd.DateOffset(seconds=period)
            return self.raw_md[
                (self.raw_md.index >= cur_time) & (self.raw_md.index <= end_time)
            ]
        elif mds is not None:
            end_index = self.current_index + mds + 1
            return self.raw_md.iloc[self.current_index : end_index]
        else:
            raise ValueError("One of 'period' or 'mds' must be provided.")

    def finish_current_md(self) -> bool:
        self.current_index += 1
        return self.current_index < len(self.raw_md)
