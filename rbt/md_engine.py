import datetime
import pandas as pd

class MdEngine(object):
    def __init__(self) -> None:
        self.date = None
        self.raw_md = None
        self.current_index = 0 

    def prepare_data(self, date: datetime.date):
        raise NotImplementedError("Subclasses should implement this method.")

    def _register_raw_md(self, raw_md):
        if not isinstance(raw_md.index, pd.DatetimeIndex):
            raise ValueError("raw_md must be indexed by datetime.")
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
            return self.raw_md[(self.raw_md.index >= cur_time) & (self.raw_md.index <= end_time)]
        elif mds is not None:
            end_index = self.current_index + mds + 1
            return self.raw_md.iloc[self.current_index:end_index]
        else:
            raise ValueError("One of 'period' or 'mds' must be provided.")
        
    def finish_current_md(self) -> bool:
        self.current_index += 1
        return self.current_index < len(self.raw_md)