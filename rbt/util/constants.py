# TODO: 加入合约信息生效日期，支持按日期查询历史合约参数
instrument_info = {
    # ==================== CFFEX 中国金融期货交易所 ====================
    "IC": {
        "name": "中证500指数", "exchange": "CFFEX",
        "tick_size": 0.2, "hands": 200, "digits": 1,
    },
    "IF": {
        "name": "沪深300指数", "exchange": "CFFEX",
        "tick_size": 0.2, "hands": 300, "digits": 1,
    },
    "IH": {
        "name": "上证50指数", "exchange": "CFFEX",
        "tick_size": 0.2, "hands": 300, "digits": 1,
    },
    "IM": {
        "name": "中证1000指数", "exchange": "CFFEX",
        "tick_size": 0.2, "hands": 200, "digits": 1,
    },
    "T": {
        "name": "10年期国债期货", "exchange": "CFFEX",
        "tick_size": 0.005, "hands": 10000, "digits": 3,
    },
    "TF": {
        "name": "5年期国债期货", "exchange": "CFFEX",
        "tick_size": 0.005, "hands": 10000, "digits": 3,
    },
    "TL": {
        "name": "30年期国债期货", "exchange": "CFFEX",
        "tick_size": 0.01, "hands": 10000, "digits": 2,
    },
    "TS": {
        "name": "2年期国债期货", "exchange": "CFFEX",
        "tick_size": 0.002, "hands": 20000, "digits": 3,
    },
    # ==================== SHFE 上海期货交易所 ====================
    "AD": {
        "name": "铝合金", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 10, "digits": 0,
    },
    "AG": {
        "name": "白银", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 15, "digits": 0,
    },
    "AL": {
        "name": "铝", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "AO": {
        "name": "氧化铝", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "AU": {
        "name": "黄金", "exchange": "SHFE",
        "tick_size": 0.02, "hands": 1000, "digits": 2,
    },
    "BR": {
        "name": "丁二烯橡胶", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "BU": {
        "name": "石油沥青", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "CU": {
        "name": "铜", "exchange": "SHFE",
        "tick_size": 10.0, "hands": 5, "digits": 0,
    },
    "FU": {
        "name": "燃料油", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "HC": {
        "name": "热轧卷板", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "NI": {
        "name": "镍", "exchange": "SHFE",
        "tick_size": 10.0, "hands": 1, "digits": 0,
    },
    "OP": {
        "name": "胶版纸", "exchange": "SHFE",
        "tick_size": 2.0, "hands": 40, "digits": 0,
    },
    "PB": {
        "name": "铅", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "RB": {
        "name": "螺纹钢", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "RU": {
        "name": "天然橡胶", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 10, "digits": 0,
    },
    "SN": {
        "name": "锡", "exchange": "SHFE",
        "tick_size": 10.0, "hands": 1, "digits": 0,
    },
    "SP": {
        "name": "漂针浆", "exchange": "SHFE",
        "tick_size": 2.0, "hands": 10, "digits": 0,
    },
    "SS": {
        "name": "不锈钢", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "WR": {
        "name": "线材", "exchange": "SHFE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "ZN": {
        "name": "锌", "exchange": "SHFE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    # ==================== DCE 大连商品交易所 ====================
    "A": {
        "name": "黄大豆1号", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "B": {
        "name": "黄大豆2号", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "BB": {
        "name": "胶合板", "exchange": "DCE",
        "tick_size": 0.05, "hands": 500, "digits": 2,
    },
    "BZ": {
        "name": "纯苯", "exchange": "DCE",
        "tick_size": 1.0, "hands": 30, "digits": 0,
    },
    "C": {
        "name": "黄玉米", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "CS": {
        "name": "玉米淀粉", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "EB": {
        "name": "苯乙烯", "exchange": "DCE",
        "tick_size": 1.0, "hands": 5, "digits": 0,
    },
    "EG": {
        "name": "乙二醇", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "FB": {
        "name": "纤维板", "exchange": "DCE",
        "tick_size": 0.5, "hands": 10, "digits": 1,
    },
    "I": {
        "name": "铁矿石", "exchange": "DCE",
        "tick_size": 0.5, "hands": 100, "digits": 1,
    },
    "J": {
        "name": "冶金焦炭", "exchange": "DCE",
        "tick_size": 0.5, "hands": 100, "digits": 1,
    },
    "JD": {
        "name": "鸡蛋", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "JM": {
        "name": "焦煤", "exchange": "DCE",
        "tick_size": 0.5, "hands": 60, "digits": 1,
    },
    "L": {
        "name": "线型低密度聚乙烯", "exchange": "DCE",
        "tick_size": 1.0, "hands": 5, "digits": 0,
    },
    "LG": {
        "name": "原木", "exchange": "DCE",
        "tick_size": 0.5, "hands": 90, "digits": 1,
    },
    "LH": {
        "name": "生猪", "exchange": "DCE",
        "tick_size": 5.0, "hands": 16, "digits": 0,
    },
    "M": {
        "name": "豆粕", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "P": {
        "name": "棕榈油", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "PG": {
        "name": "液化石油气", "exchange": "DCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "PP": {
        "name": "聚丙烯", "exchange": "DCE",
        "tick_size": 1.0, "hands": 5, "digits": 0,
    },
    "RR": {
        "name": "粳米", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "V": {
        "name": "聚氯乙烯", "exchange": "DCE",
        "tick_size": 1.0, "hands": 5, "digits": 0,
    },
    "Y": {
        "name": "豆油", "exchange": "DCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    # ==================== CZCE 郑州商品交易所 ====================
    "AP": {
        "name": "苹果", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "CF": {
        "name": "一号棉花", "exchange": "CZCE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "CJ": {
        "name": "红枣", "exchange": "CZCE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "CY": {
        "name": "棉纱", "exchange": "CZCE",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
    "FG": {
        "name": "玻璃", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "JR": {
        "name": "粳稻", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "MA": {
        "name": "甲醇", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "OI": {
        "name": "菜籽油", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "PF": {
        "name": "短纤", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 5, "digits": 0,
    },
    "PK": {
        "name": "花生仁", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 5, "digits": 0,
    },
    "PL": {
        "name": "丙烯", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "PM": {
        "name": "普通小麦", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 50, "digits": 0,
    },
    "PR": {
        "name": "瓶片", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 15, "digits": 0,
    },
    "PX": {
        "name": "对二甲苯", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 5, "digits": 0,
    },
    "RI": {
        "name": "早籼稻", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "RM": {
        "name": "菜籽粕", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "RS": {
        "name": "油菜籽", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "SA": {
        "name": "纯碱", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "SF": {
        "name": "硅铁", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 5, "digits": 0,
    },
    "SH": {
        "name": "烧碱", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 30, "digits": 0,
    },
    "SM": {
        "name": "锰硅", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 5, "digits": 0,
    },
    "SR": {
        "name": "白砂糖", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "TA": {
        "name": "精对苯二甲酸", "exchange": "CZCE",
        "tick_size": 2.0, "hands": 5, "digits": 0,
    },
    "UR": {
        "name": "尿素", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "WH": {
        "name": "优质强筋小麦", "exchange": "CZCE",
        "tick_size": 1.0, "hands": 20, "digits": 0,
    },
    "ZC": {
        "name": "动力煤", "exchange": "CZCE",
        "tick_size": 0.2, "hands": 100, "digits": 1,
    },
    # ==================== INE 上海国际能源交易中心 ====================
    "BC": {
        "name": "国际铜", "exchange": "INE",
        "tick_size": 10.0, "hands": 5, "digits": 0,
    },
    "EC": {
        "name": "SCFIS欧线", "exchange": "INE",
        "tick_size": 0.1, "hands": 50, "digits": 1,
    },
    "LU": {
        "name": "低硫燃料油", "exchange": "INE",
        "tick_size": 1.0, "hands": 10, "digits": 0,
    },
    "NR": {
        "name": "20号胶", "exchange": "INE",
        "tick_size": 5.0, "hands": 10, "digits": 0,
    },
    "SC": {
        "name": "原油", "exchange": "INE",
        "tick_size": 0.1, "hands": 1000, "digits": 1,
    },
    # ==================== GFEX 广州期货交易所 ====================
    "LC": {
        "name": "碳酸锂", "exchange": "GFEX",
        "tick_size": 20.0, "hands": 1, "digits": 0,
    },
    "PD": {
        "name": "钯", "exchange": "GFEX",
        "tick_size": 0.05, "hands": 1000, "digits": 2,
    },
    "PS": {
        "name": "多晶硅", "exchange": "GFEX",
        "tick_size": 5.0, "hands": 3, "digits": 0,
    },
    "PT": {
        "name": "铂", "exchange": "GFEX",
        "tick_size": 0.05, "hands": 1000, "digits": 2,
    },
    "SI": {
        "name": "工业硅", "exchange": "GFEX",
        "tick_size": 5.0, "hands": 5, "digits": 0,
    },
}
