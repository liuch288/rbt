import datetime
import pandas as pd


class MdEngine(object):
    """
    用户继承MdEngine类，修改构造函数和prepare_data函数。
    在prepare_data函数中，用户需要将数据读取出来，改变列名为特定格式（必须包含sym、bid_px等列），并以Timestamp作为index。
    在prepare_data完成后，要触发_register_raw_md函数来保存处理好的数据表。
    市价单拆分功能已独立为MoSplitDMU，如需使用请在策略中注册该DMU。
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
            ].copy()
        elif mds is not None:
            end_index = self.current_index + mds + 1
            return self.raw_md.iloc[self.current_index : end_index].copy()
        else:
            raise ValueError("One of 'period' or 'mds' must be provided.")

    def finish_current_md(self) -> bool:
        self.current_index += 1
        return self.current_index < len(self.raw_md)
