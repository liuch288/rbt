import unittest

from IndexCalculator import *


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


class TestSum(unittest.TestCase):
    def test_initialization(self):
        """测试初始化"""
        period = 5
        sum_calculator = Sum(period)
        self.assertEqual(sum_calculator.period, period)
        self.assertEqual(sum_calculator.result, 0)
        self.assertEqual(len(sum_calculator.data), 0)

    def test_update_with_less_than_period(self):
        """测试更新数据，数据点少于周期"""
        period = 5
        sum_calculator = Sum(period)
        for i in range(1, 4):
            sum_calculator.update(i)
            self.assertEqual(sum_calculator.result, sum(range(1, i + 1)))

    def test_update_with_exactly_period(self):
        """测试更新数据，数据点等于周期"""
        period = 3
        sum_calculator = Sum(period)
        for i in range(1, period + 1):
            sum_calculator.update(i)
        self.assertEqual(sum_calculator.result, sum(range(1, period + 1)))

    def test_update_with_more_than_period(self):
        """测试更新数据，数据点超过周期"""
        period = 3
        sum_calculator = Sum(period)
        for i in range(1, 7):
            sum_calculator.update(i)
        # 最后三个数据点的和应该是 4 + 5 + 6 = 15
        self.assertEqual(sum_calculator.result, 15)

    def test_reset(self):
        """测试重置"""
        period = 3
        sum_calculator = Sum(period)
        for i in range(1, 4):
            sum_calculator.update(i)
        sum_calculator.reset()
        self.assertEqual(sum_calculator.result, None)
        self.assertEqual(len(sum_calculator.data), 0)


if __name__ == "__main__":
    unittest.main()
