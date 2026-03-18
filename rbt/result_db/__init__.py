"""ResultDB 模块 - 提供多种 ResultDB 实现"""

from .pkl_result_db import PklResultDB, ResultDB

# 向后兼容: ResultDB = PklResultDB
__all__ = ["ResultDB", "PklResultDB"]
