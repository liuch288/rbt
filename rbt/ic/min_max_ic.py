from .index_calculator import IndexCalculator

class MinMaxIC(IndexCalculator):
    def __init__(self):
        super().__init__(1)
        self.min_value = float('inf')  # 初始化为正无穷大
        self.max_value = float('-inf')  # 初始化为负无穷大

    def calculate(self, new_data):
        if new_data < self.min_value:
            self.min_value = new_data

        if new_data > self.max_value:
            self.max_value = new_data

        self.result = {"min": self.min_value, "max": self.max_value}

    def reset(self):
        super().reset()
        self.min_value = float('inf')  # 重置为正无穷大
        self.max_value = float('-inf')  # 重置为负无穷大


# if __name__ == "__main__":
#     import unittest

#     class TestMinMaxIC(unittest.TestCase):
#         def setUp(self):
#             self.ic = MinMaxIC()

#         def test_initial_values(self):
#             self.assertEqual(self.ic.min_value, float('inf'))
#             self.assertEqual(self.ic.max_value, float('-inf'))
#             self.assertEqual(self.ic.result, None)

#         def test_single_value(self):
#             self.ic.calculate(10)
#             self.assertEqual(self.ic.min_value, 10)
#             self.assertEqual(self.ic.max_value, 10)
#             self.assertEqual(self.ic.result, {"min": 10, "max": 10})

#         def test_multiple_values(self):
#             data = [10, 5, 20, 3, 15]
#             expected_min = 3
#             expected_max = 20
#             for value in data:
#                 self.ic.calculate(value)
            
#             self.assertEqual(self.ic.min_value, expected_min)
#             self.assertEqual(self.ic.max_value, expected_max)
#             self.assertEqual(self.ic.result, {"min": expected_min, "max": expected_max})

#         def test_reset(self):
#             data = [10, 5, 20]
#             for value in data:
#                 self.ic.calculate(value)
            
#             self.ic.reset()
#             self.assertEqual(self.ic.min_value, float('inf'))
#             self.assertEqual(self.ic.max_value, float('-inf'))
#             self.assertEqual(self.ic.result, None)

#         def test_all_same_values(self):
#             data = [10, 10, 10, 10]
#             expected_min = 10
#             expected_max = 10
#             for value in data:
#                 self.ic.calculate(value)
            
#             self.assertEqual(self.ic.min_value, expected_min)
#             self.assertEqual(self.ic.max_value, expected_max)
#             self.assertEqual(self.ic.result, {"min": expected_min, "max": expected_max})

#     unittest.main()