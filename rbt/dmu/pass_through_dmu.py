"""
PassThroughDMU - 将原始行情数据直接存入ResultDB
用于将原始数据和处理后的数据放在一起
"""

from rbt.dmu import DecisionMakingUnit


class PassThroughDMU(DecisionMakingUnit):
    """PassThrough DMU - 将原始tick数据的关键字段存入ResultDB"""
    
    version = "v1"

    def __init__(self, fields=None):
        """
        初始化PassThroughDMU。
        
        参数:
            fields (list): 要保存的字段列表，默认为None（保存所有字段）
        """
        super().__init__()
        # 默认保存的原始字段
        self.fields = fields
        self.update_unit_name()

    def get_param_str(self) -> str:
        if self.fields:
            return f"{len(self.fields)}fields"
        return "all"

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        result = {}
        if self.fields:
            # 只保存指定的字段
            for field in self.fields:
                if field in new_data:
                    result[field] = new_data[field]
        else:
            # 保存所有字段
            for field in new_data.keys():
                result[field] = new_data[field]
        return result


# 测试
if __name__ == "__main__":
    import datetime
    
    dmu = PassThroughDMU()
    
    # 模拟tick数据
    tick = {
        "name": datetime.datetime(2026, 1, 5, 9, 30),
        "last_px": 111.65,
        "tot_sz": 1000,
        "bid1": 111.60, "ask1": 111.65,
        "bid_vol1": 50, "ask_vol1": 30,
    }
    
    result = dmu.make_decision(tick)
    print("PassThrough result:", result)
