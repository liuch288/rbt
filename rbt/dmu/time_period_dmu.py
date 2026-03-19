"""
TimePeriodDMU - 根据时间划分交易时间段
用于将每天的交易时间划分为不同的时间段：
- 9:00-9:45 → A
- 9:45-10:00 → B
- 10:00-11:00 → C
- 11:00-12:00 → D
- 12:00-13:15 → E
- 13:15-14:45 → F
- 14:45-15:15 → G
- 其他时间 → Z
"""

import datetime
from rbt.dmu import DecisionMakingUnit


class TimePeriodDMU(DecisionMakingUnit):
    """Time Period DMU - 根据时间划分交易时间段"""
    
    version = "v1"

    # 时间段定义: (开始时间, 结束时间, 标识)
    PERIODS = [
        (datetime.time(9, 0), datetime.time(9, 45), "A"),
        (datetime.time(9, 45), datetime.time(10, 0), "B"),
        (datetime.time(10, 0), datetime.time(11, 0), "C"),
        (datetime.time(11, 0), datetime.time(12, 0), "D"),
        (datetime.time(12, 0), datetime.time(13, 15), "E"),
        (datetime.time(13, 15), datetime.time(14, 45), "F"),
        (datetime.time(14, 45), datetime.time(15, 15), "G"),
    ]

    def __init__(self):
        """
        初始化TimePeriodDMU。
        """
        super().__init__()

    def _get_period(self, current_time: datetime.datetime) -> str:
        """
        根据时间戳获取当前所属的时间段。
        
        参数:
            current_time: datetime 类型的时间戳
            
        返回:
            时间段标识 (A-G)，如果不在任何时间段内返回 Z
        """
        time_only = current_time.time()
        
        for start_time, end_time, period in self.PERIODS:
            if start_time <= time_only < end_time:
                return period
        
        return "Z"

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        """
        根据市场数据中的时间戳确定当前所属的交易时间段。
        
        参数:
            new_data: 市场数据，new_data.name 为 datetime 类型的时间戳
            previous_result: 之前的决策结果（可选）
            
        返回:
            包含当前时间段标识的字典，例如: {"period": "A"}
        """
        current_time = new_data.name
        period = self._get_period(current_time)
        
        return {"period": period}


# 测试
if __name__ == "__main__":
    dmu = TimePeriodDMU()
    
    # 测试各个时间段
    test_times = [
        datetime.datetime(2026, 1, 5, 9, 0),   # A
        datetime.datetime(2026, 1, 5, 9, 30),   # A
        datetime.datetime(2026, 1, 5, 9, 44),   # A
        datetime.datetime(2026, 1, 5, 9, 45),   # B
        datetime.datetime(2026, 1, 5, 9, 59),   # B
        datetime.datetime(2026, 1, 5, 10, 0),   # C
        datetime.datetime(2026, 1, 5, 10, 30),  # C
        datetime.datetime(2026, 1, 5, 11, 0),    # D
        datetime.datetime(2026, 1, 5, 11, 30),  # D
        datetime.datetime(2026, 1, 5, 12, 0),   # E
        datetime.datetime(2026, 1, 5, 12, 30),  # E
        datetime.datetime(2026, 1, 5, 13, 15),  # F
        datetime.datetime(2026, 1, 5, 14, 0),   # F
        datetime.datetime(2026, 1, 5, 14, 45),  # G
        datetime.datetime(2026, 1, 5, 15, 0),   # G
        datetime.datetime(2026, 1, 5, 15, 14),  # G
        datetime.datetime(2026, 1, 5, 15, 15),  # Z (收盘后)
        datetime.datetime(2026, 1, 5, 8, 59),   # Z (开盘前)
    ]
    
    for ts in test_times:
        tick = {"name": ts}
        result = dmu.make_decision(tick)
        print(f"{ts.strftime('%H:%M:%S')} -> {result}")
