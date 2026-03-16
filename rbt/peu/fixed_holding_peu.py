"""
固定持有期限收益评估单元 (FixedHoldingPEU)

本模块定义了 FixedHoldingPEU 类，用于评估固定持有期限的收益情况。
该 PEU 计算从数据起点到终点的收益，以及周期内的最大波幅。

计算指标：
1. pnl: 最后中间价相比第一个中间价的变化（百分比）
2. long_return: 做多收益 = (最后bid - 第一个ask) / 第一个ask（对手价开仓，对手价平仓）
3. short_return: 做空收益 = (第一个bid - 最后ask) / 第一个bid（对手价开仓，对手价平仓）
4. max_up_vol: 向上最大波幅 = (周期内最高价 - 第一中间价) / 第一中间价
5. max_down_vol: 向下最大波幅 = (第一中间价 - 周期内最低价) / 第一中间价

中间价 = (ask_px1 + bid_px1) / 2
最高价 = ask_px1（卖一价，假设为周期内最高价）
最低价 = bid_px1（买一价，假设为周期内最低价）

Version:
    v1 - 初始版本
"""

from .pnl_estimate_unit import PnlEstimateUnit


class FixedHoldingPEU(PnlEstimateUnit):
    """
    固定持有期限收益评估单元
    
    用于评估在固定持有期限内的收益情况。
    计算做多/做空收益以及周期内的最大波幅。
    不涉及实际交易成交模拟，仅计算理论收益。
    
    Attributes:
        version: PEU 版本号标识
        
    Example:
        >>> peu = FixedHoldingPEU()
        >>> result = peu.estimate(data)
        >>> print(result)
        {'pnl': 0.05, 'long_return': 0.05, 'short_return': -0.05, 
         'max_up_vol': 0.10, 'max_down_vol': 0.08}
    """

    version = "v1"

    def __init__(self, watching_time: float = None, watching_mds: int = None):
        """
        初始化固定持有期限收益评估单元
        
        Args:
            watching_time: 观察时长（秒），表示从数据开头开始观察的时长。
                           与 watching_mds 参数二选一使用，不能同时指定。
            watching_mds: 观察行情数据点个数，表示从数据开头开始观察的行情数据条数。
                          与 watching_time 参数二选一使用，不能同时指定。
        """
        super().__init__(watching_time=watching_time, watching_mds=watching_mds)

    def estimate(self, data, previous_result: dict = {}) -> dict:
        """
        评估固定持有期限的收益
        
        计算以下指标：
        - pnl: 最后中间价相比第一个中间价的变化百分比
        - long_return: 做多收益（百分比）= (最后bid - 第一个ask) / 第一个ask
        - short_return: 做空收益（百分比）= (第一个bid - 最后ask) / 第一个bid
        - max_up_vol: 向上最大波幅（百分比）
        - max_down_vol: 向下最大波幅（百分比）
        
        Args:
            data: pandas.DataFrame，包含行情数据。
                  必须包含列：ask_px1（卖一价）、bid_px1（买一价）
            previous_result: dict，可选的上一轮评估结果（当前未使用）
        
        Returns:
            dict: 包含以下字段的评估结果：
                - pnl (float): 最后中间价相比第一中间价的变化百分比
                - long_return (float): 做多收益百分比（对手价开仓，对手价平仓）
                - short_return (float): 做空收益百分比（对手价开仓，对手价平仓）
                - max_up_vol (float): 向上最大波幅百分比
                - max_down_vol (float): 向下最大波幅百分比
                - first_mid_px (float): 第一个数据点的中间价
                - last_mid_px (float): 最后一个数据点的中间价
                - first_ask (float): 第一个ask价
                - first_bid (float): 第一个bid价
                - last_ask (float): 最后一个ask价
                - last_bid (float): 最后一个bid价
                - period_high (float): 周期内最高价（ask_px1 最大值）
                - period_low (float): 周期内最低价（bid_px1 最小值）
        
        Raises:
            ValueError: 当数据为空或缺少必要列时抛出
        
        Note:
            - 中间价 = (ask_px1 + bid_px1) / 2
            - 最高价使用周期内的 ask_px1 最大值
            - 最低价使用周期内的 bid_px1 最小值
            - 所有收益和波幅均为百分比形式（如 0.05 表示 5%）
        """
        # 检查数据是否为空
        if data is None or len(data) == 0:
            raise ValueError("数据不能为空")
        
        # 检查必要列是否存在
        required_columns = ['ask_px1', 'bid_px1']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据中缺少必要列: {col}")
        
        # 计算中间价
        # 中间价 = (卖一价 + 买一价) / 2
        data = data.copy()
        data['mid_px'] = (data['ask_px1'] + data['bid_px1']) / 2
        
        # 获取第一个和最后一个数据点
        first_data = data.iloc[0]
        last_data = data.iloc[-1]
        
        # 提取价格
        first_ask = first_data['ask_px1']  # 第一个ask（开多仓价 / 平空仓价）
        first_bid = first_data['bid_px1']  # 第一个bid（开空仓价 / 平多仓价）
        last_ask = last_data['ask_px1']    # 最后一个ask（平空仓价）
        last_bid = last_data['bid_px1']    # 最后一个bid（平多仓价）
        
        # 周期内最高价（使用 ask_px1 的最大值）
        period_high = data['ask_px1'].max()
        
        # 周期内最低价（使用 bid_px1 的最小值）
        period_low = data['bid_px1'].min()
        
        # 第一中间价（用于波幅计算）
        first_mid_px = (first_ask + first_bid) / 2
        last_mid_px = (last_ask + last_bid) / 2
        
        # 避免除零错误
        if first_ask == 0:
            raise ValueError("第一个ask价为0，无法计算做多收益")
        if first_bid == 0:
            raise ValueError("第一个bid价为0，无法计算做空收益")
        
        # 1. pnl：最后中间价相比第一个中间价的变化（百分比）
        pnl = (last_mid_px - first_mid_px) / first_mid_px
        
        # 2. 做多收益：(最后bid - 第一个ask) / 第一个ask（对手价开仓，对手价平仓）
        long_return = (last_bid - first_ask) / first_ask
        
        # 3. 做空收益：(第一个bid - 最后ask) / 第一个bid（对手价开仓，对手价平仓）
        short_return = (first_bid - last_ask) / first_bid
        
        # 4. 向上最大波幅：(周期内最高价 - 第一中间价) / 第一中间价
        max_up_vol = (period_high - first_mid_px) / first_mid_px
        
        # 5. 向下最大波幅：(第一中间价 - 周期内最低价) / 第一中间价
        max_down_vol = (first_mid_px - period_low) / first_mid_px
        
        return {
            'pnl': pnl,
            'long_return': long_return,
            'short_return': short_return,
            'max_up_vol': max_up_vol,
            'max_down_vol': max_down_vol,
            'first_mid_px': first_mid_px,
            'last_mid_px': last_mid_px,
            'first_ask': first_ask,
            'first_bid': first_bid,
            'last_ask': last_ask,
            'last_bid': last_bid,
            'period_high': period_high,
            'period_low': period_low,
        }
