import unittest
import pandas as pd

from rbt.realtime_strategy import RealtimeStrategy
from rbt.dmu import DecisionMakingUnit


class MockDMU(DecisionMakingUnit):
    version = "v1"
    
    def make_decision(self, new_md, previous_result: dict = {}) -> dict:
        return {"signal": new_md["price"] * 2}


class TestRealtimeStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = RealtimeStrategy()
        self.strategy.register_dmu(MockDMU())

    def test_run_once_basic(self):
        new_md = pd.Series({"price": 100, "volume": 1000})
        result = self.strategy.run_once(new_md)
        
        self.assertIn("MockDMU_v1_signal", result)
        self.assertEqual(result["MockDMU_v1_signal"], 200)

    def test_run_once_with_bgm(self):
        new_md = pd.Series({"price": 100})
        bgm = {"date": "2026-03-05", "factor": 1.5}
        
        result = self.strategy.run_once(new_md, bgm=bgm)
        
        self.assertEqual(result["date"], "2026-03-05")
        self.assertEqual(result["factor"], 1.5)
        self.assertIn("MockDMU_v1_signal", result)


if __name__ == "__main__":
    unittest.main()
