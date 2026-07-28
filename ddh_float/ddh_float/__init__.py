"""
DDH-Float: Tagged-Residue Floating-Point Arithmetic
面向确定性计算的带标签余数浮点算术模型

快速开始:
    >>> from ddh_float import DDHNumber
    >>> x = DDHNumber(1, 3, 16)  # 1/3, Ω=16
    >>> print(x)
    1/3 = 0.3333333333333333 + 0.3333333333333333x (Ω=16)

作者: 刘一京 (Yijing Liu)
许可: MIT License
"""

from ._core import DDHNumber

__version__ = "1.0.0"
__author__ = "Yijing Liu"
__license__ = "MIT"

__all__ = ["DDHNumber"]
