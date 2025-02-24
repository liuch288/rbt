import unittest
from datetime import datetime, timedelta

import pandas as pd

from rbt.ic import *
from rbt.dmu import *


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


class TestMosRecoverICLv2(unittest.TestCase):
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

    def compare_lists(self, lst1, lst2):
        sorted_lst1 = sorted([tuple(sorted(d.items())) for d in lst1])
        sorted_lst2 = sorted([tuple(sorted(d.items())) for d in lst2])
        return sorted_lst1 == sorted_lst2

    def test_recover_tick_size(self):
        recover = MosRecoverIC(0.01, 10000)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 3)
        ans = [
            {"side": "sell", "price": 108.93, "volume": 10},
            {"side": "sell", "price": 108.92, "volume": 5},
            {"side": "sell", "price": 108.94, "volume": 9},
        ]
        self.assertTrue(self.compare_lists(result, ans))

    def test_recover_sym(self):
        recover = MosRecoverIC(sym="tl2412")
        self.assertEqual(recover.tick_size, 0.01)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 3)


class TestMosRecoverICLv1(unittest.TestCase):
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
        }
    )
    cur_lob = MdShell(
        {
            "bid_px1": 108.92,
            "ask_px1": 108.93,
            "trade_sz": 24.0,
            "trade_notional": 26143600.0,
        }
    )

    def compare_lists(self, lst1, lst2):
        sorted_lst1 = sorted([tuple(sorted(d.items())) for d in lst1])
        sorted_lst2 = sorted([tuple(sorted(d.items())) for d in lst2])
        return sorted_lst1 == sorted_lst2

    def test_recover_tick_size(self):
        recover = MosRecoverIC(0.01, 10000, md_type="lv1")
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 2)
        ans = [
            {"side": "sell", "price": 108.93, "volume": 20},
            {"side": "sell", "price": 108.94, "volume": 4},
        ]
        self.assertTrue(self.compare_lists(ans, result))

    def test_recover_sym(self):
        recover = MosRecoverIC(sym="tl2412", md_type="lv1")
        self.assertEqual(recover.tick_size, 0.01)
        self.assertEqual(recover.update(self.last_lob), [])
        result = recover.update(self.cur_lob)
        self.assertEqual(len(result), 2)


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


class TestRollingKlineIC(unittest.TestCase):
    def test_calculate(self):
        # 创建KlineIC实例
        kline_ic = RollingKlineIC(period=5)

        # 添加测试数据
        test_data = [100, 102, 101, 105, 103]
        for data in test_data:
            kline_ic.update(data)

        # 调用calculate方法
        kline_ic.calculate(None)

        # 检查初始结果
        expected_result = {"open": 100, "close": 103, "high": 105, "low": 100}
        self.assertEqual(kline_ic.result, expected_result)

        # 添加新数据并移除旧数据
        new_data = 106
        kline_ic.update(new_data)

        # 再次调用calculate方法
        kline_ic.calculate(None)

        # 检查更新后的结果
        expected_result = {"open": 102, "close": 106, "high": 106, "low": 101}
        self.assertEqual(kline_ic.result, expected_result)


class TestOlsTrendIC(unittest.TestCase):
    def setUp(self):
        # 基准时间
        self.test_start_time = datetime.now()

        # 初始化OlsTrendIC实例
        self.ic = OlsTrendIC(window_size=5)

        # 准备测试数据
        self.test_data = [
            {"time": self.test_start_time, "value": 1.0},
            {"time": self.test_start_time + timedelta(seconds=1), "value": 2.0},
            {"time": self.test_start_time + timedelta(seconds=2), "value": 3.0},
            {"time": self.test_start_time + timedelta(seconds=3), "value": 4.0},
            {"time": self.test_start_time + timedelta(seconds=4), "value": 5.0},
            {"time": self.test_start_time + timedelta(seconds=5), "value": 6.0},
        ]

    def test_ols_trend_ic(self):
        # 逐步添加数据点
        for data in self.test_data:
            self.ic.update(data)

        # 检查结果
        result = self.ic.result
        self.assertIsNotNone(result)  # 确保结果不为None
        self.assertEqual(result["window_size"], 5)  # 确保窗口大小正确
        self.assertAlmostEqual(result["coefficient"], 1.0)  # 确保系数接近1.0
        self.assertAlmostEqual(result["intercept"], 6.0)  # 确保截距接近1.0
        self.assertLess(result["mse"], 1e-8)  # 确保MSE较小
        self.assertLess(1 - result["r_squared"], 1e-8)  # 确保R²接近1.0

        self.ic.update(
            {"time": self.test_start_time + timedelta(seconds=6), "value": 5.0}
        )
        # 检查结果
        result = self.ic.result
        self.assertAlmostEqual(result["coefficient"], 0.7142857142857134)
        self.assertAlmostEqual(result["intercept"], 5.952380952380952)
        self.assertAlmostEqual(result["mse"], 0.3174603174603175)
        self.assertAlmostEqual(result["r_squared"], 0.8241758241758241)


class TestPriceFrequencyIC(unittest.TestCase):

    def setUp(self):
        # 在每个测试方法之前执行
        self.period = 3
        self.ic = PriceFrequencyIC(self.period)

    def test_initialization(self):
        # 测试初始化
        self.assertEqual(self.ic.period, self.period)
        self.assertEqual(self.ic.price_counts, {})
        self.assertEqual(self.ic.result, None)

    def test_update(self):
        # 测试更新方法
        test_data = [1, 2, 3, 2, 1]
        expected_results = [
            {1: 1},  # 添加第一个数据
            {1: 1, 2: 1},  # 添加第二个数据
            {1: 1, 2: 1, 3:1},  # 添加第三个数据，第二个数据频数增加
            {2: 2, 3: 1},  # 移除第一个数据，添加第四个数据
            {2: 1, 3: 1, 1: 1}  # 添加第五个数据
        ]

        for i, data in enumerate(test_data):
            self.ic.update(data)
            self.assertEqual(self.ic.result, expected_results[i])

    def test_reset(self):
        # 测试重置方法
        self.ic.update(1)
        self.ic.update(2)
        self.ic.reset()
        self.assertEqual(self.ic.price_counts, {})
        self.assertEqual(self.ic.result, {})


class TestPositionGenDMU(unittest.TestCase):

    def test_add_rule(self):
        dmu = PositionGenDMU()
        dmu.add_rule("rule1", 'prev_result["MA"] > 0', 1)
        dmu.add_rule(
            "rule2",
            'prev_result["KDJ"] == 0 and prev_result["std"] < 0',
            -1,
            smooth=True,
        )
        self.assertIn(("rule1", 'prev_result["MA"] > 0', 1, False), dmu.rules)
        self.assertIn(
            ("rule2", 'prev_result["KDJ"] == 0 and prev_result["std"] < 0', -1, True),
            dmu.rules,
        )
        self.assertTrue(isinstance(dmu.smoother["rule2"], SmoothIC))

    def test_make_decision_single_rule(self):
        dmu = PositionGenDMU()
        dmu.add_rule("rule1", 'prev_result["MA"] > 0', 1)
        decision = dmu.on_market_data(None, {"MA": 0.5})
        self.assertEqual(decision["rule1_position"], 1)
        decision = dmu.on_market_data(None, {"MA": -0.5})
        self.assertEqual(decision["rule1_position"], 0)

    def test_make_decision_multiple_rules(self):
        dmu = PositionGenDMU()
        dmu.add_rule("rule1", 'prev_result["MA"] > 0', 1)
        dmu.add_rule("rule2", 'prev_result["KDJ"] == 0 and prev_result["std"] < 0', -1)
        decision = dmu.on_market_data(None, {"MA": 0.5, "KDJ": 0, "std": -0.5})
        self.assertEqual(decision["rule1_position"], 1)
        self.assertEqual(decision["rule2_position"], -1)
        decision = dmu.on_market_data(None, {"MA": -0.5, "KDJ": 1, "std": 0.5})
        self.assertEqual(decision["rule1_position"], 0)
        self.assertEqual(decision["rule2_position"], 0)

    def test_make_decision_multiple_rules_smooth(self):
        dmu = PositionGenDMU()
        dmu.add_rule("rule1", 'prev_result["MA"] > 0', 1, True)
        dmu.add_rule("rule2", 'prev_result["KDJ"] == 0 and prev_result["std"] < 0', -1)
        decision = dmu.on_market_data(None, {"MA": 0.5, "KDJ": 0, "std": -0.5})
        decision = dmu.on_market_data(None, {"MA": 0.5, "KDJ": 0, "std": -0.5})
        self.assertEqual(decision["rule1_position"], 1)
        self.assertEqual(decision["rule2_position"], -1)
        decision = dmu.on_market_data(None, {"MA": -0.5, "KDJ": 1, "std": 0.5})
        self.assertEqual(decision["rule1_position"], 1)
        self.assertEqual(decision["rule2_position"], 0)

    def test_make_decision_with_invalid_rule(self):
        dmu = PositionGenDMU()
        dmu.add_rule("rule1", 'prev_result["MA"] > 0', 1)
        dmu.add_rule("rule2", 'prev_result["KDJ"] / 0', -1)
        decision = dmu.on_market_data(None, {"MA": 0.5, "KDJ": 0})
        self.assertEqual(decision["rule1_position"], 1)
        self.assertEqual(decision["rule2_position"], 0)


if __name__ == "__main__":
    unittest.main()
