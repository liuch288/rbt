import os


class ResultDB(object):
    """
    由于PEU的运算通常极为缓慢，因此需要缓存前期计算好的数据用于后续研究。
    ResultDB负责管理已有结果，所有数据以“sym_date.pkl”的形式存放，datetime.da
    """

    def __init__(self, data_path):
        if os.path.exists(data_path):
            self.data_path = data_path
        else:
            raise FileNotFoundError(f"{data_path} not found.")
    
    def query_columns():
        return None