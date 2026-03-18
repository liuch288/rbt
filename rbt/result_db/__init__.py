"""ResultDB 模块 - 提供多种 ResultDB 实现"""

from .fs_result_db import FsResultDB
from .pkl_result_db import PklResultDB, ResultDB

# 向后兼容: ResultDB = PklResultDB
__all__ = ["ResultDB", "PklResultDB", "FsResultDB"]
