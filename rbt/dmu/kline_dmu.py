from rbt.dmu import DecisionMakingUnit
import datetime


class KlineDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self, interval: int = 1, start_time: datetime.time = None):
        """
        初始化KlineDMU。

        参数:
            interval (int): K线的时间间隔，单位为分钟，默认为1分钟。
            start_time (datetime.time): K线开始时间，默认为9:30。
        """
        super().__init__()
        self.interval = interval  # K线时间间隔
        self.start_time = start_time or datetime.time(9, 30)  # K线开始时间
        self.current_kline_end = None  # 当前K线结束时间
        self.kline_init_volume = None  # K线开始时的累计成交量
        self.kline_init_oi = None  # K线开始时的持仓量
        self.kline_open = None  # K线开盘价
        self.kline_high = None  # K线最高价
        self.kline_low = None  # K线最低价
        self.kline_close = None  # K线收盘价
        self.kline_volume = None  # K线成交量
        self.kline_oi_diff = None  # K线持仓量变动

    def on_end_of_day(self):
        """日终重置K线状态"""
        self.current_kline_end = None
        self.kline_init_volume = None
        self.kline_init_oi = None
        self.kline_open = None
        self.kline_high = None
        self.kline_low = None
        self.kline_close = None
        self.kline_volume = None
        self.kline_oi_diff = None

    def get_param_str(self):
        """
        生成参数信息，用于更新单元名称。

        Returns:
            str: 载明参数的字符串。
        """
        return f"{self.interval}min"

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        current_time = new_data.name  # 当前时间
        cumulative_volume = new_data["tot_sz"]
        cumulative_oi = new_data["oi"]
        last_price = new_data["last_px"]  # 最新价

        # 仅在初始化第一根k线的结束时间时运行
        if self.current_kline_end is None:
            self.current_kline_end = datetime.datetime.combine(
                current_time.date(), self.start_time
            )
            self.kline_open = last_price
            self.kline_high = last_price
            self.kline_low = last_price
            self.kline_close = last_price
            self.kline_init_volume = cumulative_volume
            self.kline_init_oi = cumulative_oi
            self.kline_volume = 0
            self.kline_oi_diff = 0

            # 追赶到当前时间
            while self.current_kline_end <= current_time:
                self.current_kline_end += datetime.timedelta(minutes=self.interval)

        # 如果k线走完且当前行情戳不计入k线
        if self.current_kline_end < current_time:
            # 跳到下一根K线
            while self.current_kline_end < current_time:
                self.current_kline_end += datetime.timedelta(minutes=self.interval)
            # 如果新k线没结束，则记录数据
            if current_time < self.current_kline_end:
                res = {
                    "open": self.kline_open,
                    "high": self.kline_high,
                    "low": self.kline_low,
                    "close": self.kline_close,
                    "volume": self.kline_volume,
                    "oi_diff": self.kline_oi_diff,
                    "end_time": self.current_kline_end,
                    "completed": True,
                }
                # 重置K线数据，使用当前累计值作为起点
                self.kline_open = last_price
                self.kline_high = last_price
                self.kline_low = last_price
                self.kline_close = last_price
                self.kline_volume = cumulative_volume - self.kline_init_volume
                self.kline_oi_diff = cumulative_oi - self.kline_init_oi
                self.kline_init_volume += self.kline_volume
                self.kline_init_oi += self.kline_oi_diff
                return res

        # 如果当前行情戳计入K线
        self.kline_open = last_price if self.kline_open is None else self.kline_open
        self.kline_close = last_price
        self.kline_high = (
            last_price
            if self.kline_high is None
            else max(self.kline_high, self.kline_close)
        )
        self.kline_low = (
            last_price
            if self.kline_low is None
            else min(self.kline_low, self.kline_close)
        )
        self.kline_volume = cumulative_volume - self.kline_init_volume
        self.kline_oi_diff = cumulative_oi - self.kline_init_oi

        # 如果当前时间恰好是K线结束时间
        if self.current_kline_end == current_time:
            res = {
                "open": self.kline_open,
                "high": self.kline_high,
                "low": self.kline_low,
                "close": self.kline_close,
                "volume": self.kline_volume,
                "oi_diff": self.kline_oi_diff,
                "end_time": self.current_kline_end,
                "completed": True,
            }
            # 跳到下一根K线
            while self.current_kline_end <= current_time:
                self.current_kline_end += datetime.timedelta(minutes=self.interval)
            # 重置K线数据，为下一根K线做准备
            self.kline_open = None
            self.kline_close = None
            self.kline_high = None
            self.kline_low = None
            self.kline_init_volume = cumulative_volume
            self.kline_init_oi = cumulative_oi
            return res

        res = {
            "open": self.kline_open,
            "high": self.kline_high,
            "low": self.kline_low,
            "close": self.kline_close,
            "volume": self.kline_volume,
            "oi_diff": self.kline_oi_diff,
            "end_time": self.current_kline_end,
            "completed": False,
        }
        return res


# # 示例使用
# if __name__ == "__main__":
#     kline_dmu = KlineDMU(interval=1)

#     # 模拟一些行情数据
#     tick_data_stream = [
#         {"name": datetime.datetime(2023, 4, 17, 9, 30), "last_px": 101, "tot_sz": 100, "oi": 23},
#         {"name": datetime.datetime(2023, 4, 17, 9, 30, 30), "last_px": 102, "tot_sz": 104, "oi": 25},
#         {"name": datetime.datetime(2023, 4, 17, 9, 31), "last_px": 99, "tot_sz": 105, "oi": 13},
#         {"name": datetime.datetime(2023, 4, 17, 9, 31, 15), "last_px": 105, "tot_sz": 110, "oi": 2},
#         {"name": datetime.datetime(2023, 4, 17, 9, 32), "last_px": 103, "tot_sz": 180, "oi": 23},
#         {"name": datetime.datetime(2023, 4, 17, 9, 33), "last_px": 104, "tot_sz": 190, "oi": 2},
#         {"name": datetime.datetime(2023, 4, 17, 9, 34), "last_px": 106, "tot_sz": 400, "oi": 238},
#         {"name": datetime.datetime(2023, 4, 17, 9, 35), "last_px": 107, "tot_sz": 700, "oi": 23},
#         {"name": datetime.datetime(2023, 4, 17, 9, 36), "last_px": 108, "tot_sz": 1900, "oi": 233},
#         {"name": datetime.datetime(2023, 4, 17, 9, 36, 3), "last_px": 109, "tot_sz": 3500, "oi": 23333},
#         {"name": datetime.datetime(2023, 4, 17, 10, 37), "last_px": 120, "tot_sz": 3700, "oi": 13333},
#         {"name": datetime.datetime(2023, 4, 17, 10, 38), "last_px": 109, "tot_sz": 3500, "oi": 23333},
#     ]

#     for i, tick_data in enumerate(tick_data_stream):
#         kline_result = kline_dmu.make_decision(tick_data)
#         print(f"Tick {i+1}: {tick_data}, Kline: {kline_result}")
