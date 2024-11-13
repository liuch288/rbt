import unittest

from rbt.ic import *


class TestSMA(unittest.TestCase):
    def test_initial_values(self):
        sma = SMA(period=5)
        self.assertEqual(sma.result, None)
        self.assertEqual(len(sma.data), 0)

    def test_update_with_insufficient_data(self):
        sma = SMA(period=5)
        sma.update(10)
        self.assertEqual(sma.result, 10)
        sma.update(20)
        self.assertEqual(sma.result, 15)

    def test_update_with_exact_period(self):
        sma = SMA(period=5)
        for i in range(1, 6):
            sma.update(i)
        self.assertEqual(sma.result, 3)

    def test_update_with_more_than_period(self):
        sma = SMA(period=5)
        for i in range(1, 10):
            sma.update(i)
        self.assertEqual(sma.result, 7)

    def test_reset(self):
        sma = SMA(period=5)
        for i in range(1, 6):
            sma.update(i)
        sma.reset()
        self.assertEqual(sma.result, None)
        self.assertEqual(len(sma.data), 0)


class TestSumCalculator(unittest.TestCase):
    def test_initialization(self):
        """测试初始化"""
        period = 5
        sum_calculator = SumCalculator(period)
        self.assertEqual(sum_calculator.period, period)
        self.assertEqual(sum_calculator.result, 0)
        self.assertEqual(len(sum_calculator.data), 0)

    def test_update_with_less_than_period(self):
        """测试更新数据，数据点少于周期"""
        period = 5
        sum_calculator = SumCalculator(period)
        for i in range(1, 4):
            res = sum_calculator.update(i)
            self.assertEqual(res, sum(range(1, i + 1)))

    def test_update_with_exactly_period(self):
        """测试更新数据，数据点等于周期"""
        period = 3
        sum_calculator = SumCalculator(period)
        for i in range(1, period + 1):
            res = sum_calculator.update(i)
        self.assertEqual(res, sum(range(1, period + 1)))

    def test_update_with_more_than_period(self):
        """测试更新数据，数据点超过周期"""
        period = 3
        sum_calculator = SumCalculator(period)
        for i in range(1, 7):
            sum_calculator.update(i)
        # 最后三个数据点的和应该是 4 + 5 + 6 = 15
        self.assertEqual(sum_calculator.result, 15)

    def test_reset(self):
        """测试重置"""
        period = 3
        sum_calculator = SumCalculator(period)
        for i in range(1, 4):
            sum_calculator.update(i)
        sum_calculator.reset()
        self.assertEqual(sum_calculator.result, 0)
        self.assertEqual(len(sum_calculator.data), 0)


class TestRecoverMos(unittest.TestCase):
    last_lob = {
        "bid_sz1": 4,
        "bid_px1": 108.94,
        "ask_px1": 108.95,
        "ask_sz1": 107,
        "bid_sz2": 9,
        "bid_px2": 108.93,
        "ask_px2": 108.96,
        "ask_sz2": 101,
        "bid_sz3": 70,
        "bid_px3": 108.92,
        "ask_px3": 108.97,
        "ask_sz3": 103,
        "bid_sz4": 39,
        "bid_px4": 108.91,
        "ask_px4": 108.98,
        "ask_sz4": 650,
        "bid_sz5": 175,
        "bid_px5": 108.9,
        "ask_px5": 108.99,
        "ask_sz5": 292,
    }
    cur_lob = {
        "bid_px1": 108.92,
        "ask_px1": 108.93,
        "bid_px2": 108.91,
        "ask_px2": 108.94,
        "trade_sz": 24.0,
        "trade_notional": 26143600.0,
    }

    def test_recover_tick_size(self):
        recover = RecoverMos(0.01, 10000)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 3)

    def test_recover_sym(self):
        recover = RecoverMos(sym="tl2412")
        self.assertEqual(recover.tick_size, 0.01)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
