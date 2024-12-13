import unittest

import pandas as pd

from rbt.ic import *


class TestMeanIC(unittest.TestCase):
    def test_initial_values(self):
        sma = MeanIC(period=5)
        self.assertEqual(sma.result, None)
        self.assertEqual(len(sma.data), 0)

    def test_update_with_insufficient_data(self):
        sma = MeanIC(period=5)
        sma.update(10)
        self.assertEqual(sma.result, 10)
        sma.update(20)
        self.assertEqual(sma.result, 15)

    def test_update_with_exact_period(self):
        sma = MeanIC(period=5)
        for i in range(1, 6):
            sma.update(i)
        self.assertEqual(sma.result, 3)

    def test_update_with_more_than_period(self):
        sma = MeanIC(period=5)
        for i in range(1, 10):
            sma.update(i)
        self.assertEqual(sma.result, 7)

    def test_reset(self):
        sma = MeanIC(period=5)
        for i in range(1, 6):
            sma.update(i)
        sma.reset()
        self.assertEqual(sma.result, None)
        self.assertEqual(len(sma.data), 0)


class TestSumIC(unittest.TestCase):
    def test_initialization(self):
        """测试初始化"""
        period = 5
        sum_calculator = SumIC(period)
        self.assertEqual(sum_calculator.period, period)
        self.assertEqual(sum_calculator.result, 0)
        self.assertEqual(len(sum_calculator.data), 0)

    def test_update_with_less_than_period(self):
        """测试更新数据，数据点少于周期"""
        period = 5
        sum_calculator = SumIC(period)
        for i in range(1, 4):
            res = sum_calculator.update(i)
            self.assertEqual(res, sum(range(1, i + 1)))

    def test_update_with_exactly_period(self):
        """测试更新数据，数据点等于周期"""
        period = 3
        sum_calculator = SumIC(period)
        for i in range(1, period + 1):
            res = sum_calculator.update(i)
        self.assertEqual(res, sum(range(1, period + 1)))

    def test_update_with_more_than_period(self):
        """测试更新数据，数据点超过周期"""
        period = 3
        sum_calculator = SumIC(period)
        for i in range(1, 7):
            sum_calculator.update(i)
        # 最后三个数据点的和应该是 4 + 5 + 6 = 15
        self.assertEqual(sum_calculator.result, 15)

    def test_reset(self):
        """测试重置"""
        period = 3
        sum_calculator = SumIC(period)
        for i in range(1, 4):
            sum_calculator.update(i)
        sum_calculator.reset()
        self.assertEqual(sum_calculator.result, 0)
        self.assertEqual(len(sum_calculator.data), 0)


class TestMosRecoverIC(unittest.TestCase):
    class MdShell(object):
        def __init__(self, data):
            self.data = data
            self.name = pd.Timestamp("2024-11-12 09:40:55.200000")

        def __getitem__(self, key):
            return self.data[key]

    last_lob = MdShell(
        {
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
    )
    cur_lob = MdShell(
        {
            "bid_px1": 108.92,
            "ask_px1": 108.93,
            "bid_px2": 108.91,
            "ask_px2": 108.94,
            "trade_sz": 24.0,
            "trade_notional": 26143600.0,
        }
    )

    def test_recover_tick_size(self):
        recover = MosRecoverIC(0.01, 10000)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 3)

    def test_recover_sym(self):
        recover = MosRecoverIC(sym="tl2412")
        self.assertEqual(recover.tick_size, 0.01)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 3)


class TestVarianceIC(unittest.TestCase):

    def setUp(self):
        self.period = 5
        self.variance_ic = VarianceIC(self.period)

    def test_variance_calculation(self):
        # 测试方差计算是否正确
        data_points = [1, 2, 3, 4, 5]
        expected_variances = [0.0, 0.25, 2 / 3, 1.25, 2.0]

        for i, data in enumerate(data_points):
            variance = self.variance_ic.update(data)
            self.assertAlmostEqual(variance, expected_variances[i], places=5)

    def test_data_update(self):
        # 测试数据更新是否正确
        data_points = [1, 2, 3, 4, 5, 6]
        for data in data_points:
            self.variance_ic.update(data)

        # 检查数据是否被正确替换
        self.assertNotIn(1, self.variance_ic.data)
        self.assertIn(6, self.variance_ic.data)

    def test_reset(self):
        # 测试重置方法是否正确
        data_points = [1, 2, 3, 4, 5]
        for data in data_points:
            self.variance_ic.update(data)

        self.variance_ic.reset()

        self.assertEqual(len(self.variance_ic.data), 0)
        self.assertIsNone(self.variance_ic.result)
        self.assertEqual(self.variance_ic.data_count, 0)



class TestSmoothIC(unittest.TestCase):

    def setUp(self):
        self.smooth_ic = SmoothIC()

    def test_constant_epoch(self):
        # 测试恒纪元情况
        self.smooth_ic.update(100)
        self.smooth_ic.update(100)
        self.smooth_ic.update(101)
        self.assertEqual(self.smooth_ic.result, 100)  # 应该忽略101的价格变化

    def test_chaos_epoch(self):
        # 测试乱纪元情况
        self.smooth_ic.update(100)
        self.smooth_ic.update(101)
        self.smooth_ic.update(102)
        self.assertEqual(self.smooth_ic.result, 102)  # 应该返回最新价格102

    def test_transition_to_constant_epoch(self):
        # 测试从乱纪元转换到恒纪元
        self.smooth_ic.update(100)
        self.smooth_ic.update(101)
        self.smooth_ic.update(102)
        self.smooth_ic.update(102)
        self.assertEqual(self.smooth_ic.result, 102)  # 应该进入恒纪元，忽略后续价格变化
        self.smooth_ic.update(103)
        self.assertEqual(self.smooth_ic.result, 102)  # 仍然忽略103的价格变化

    def test_reset(self):
        # 测试重置方法
        self.smooth_ic.update(100)
        self.smooth_ic.update(101)
        self.smooth_ic.reset()
        self.assertIsNone(self.smooth_ic.result)  # 结果应该为None

if __name__ == "__main__":
    unittest.main()