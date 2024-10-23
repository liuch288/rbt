import datetime
import pandas as pd

class MdEngine(object):
    def __init__(self) -> None:
        self.date = None
        self.raw_md = None
        self.current_index = 0  # 用于跟踪当前行情数据的位置

    def prepare_data(self, date: datetime.date):
        # 子类需要实现具体的数据准备逻辑
        raise NotImplementedError("Subclasses should implement this method.")

    def _register_raw_md(self, raw_md):
        # 保存raw_md，并对raw_md按时间进行排序
        if not isinstance(raw_md.index, pd.DatetimeIndex):
            raise ValueError("raw_md must be indexed by datetime.")
        self.raw_md = raw_md.sort_index().copy()
        self.current_index = 0  # 重置当前行情数据位置

    def get_next_md(self):
        # 逐行输出行情数据
        if self.raw_md is None or self.current_index >= len(self.raw_md):
            return None  # 如果没有更多数据，返回None
        next_md = self.raw_md.iloc[self.current_index]
        self.current_index += 1  # 更新当前位置
        return next_md

    def get_future_md(self, period: float = None, mds: int = None) -> pd.DataFrame:
        # 根据需要返回数据
        if period is not None and mds is not None:
            raise ValueError("Only one of 'period' or 'mds' can be provided.")
        if period is not None:
            end_time = self.raw_md.index[self.current_index] + datetime.timedelta(seconds=period)
            return self.raw_md[self.raw_md.index <= end_time]
        elif mds is not None:
            end_index = self.current_index + mds
            return self.raw_md.iloc[self.current_index:end_index]
        else:
            raise ValueError("One of 'period' or 'mds' must be provided.")