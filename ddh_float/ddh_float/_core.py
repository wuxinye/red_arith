"""
ddh_float/_core.py
===================
DDH-Float 核心数据类型

核心公理:
1. 令 x = 1/10^Ω 为最小不可分单位 (Ω 为任意正整数)
2. 任意有理数 a/b = M + k·x
   - M 为主部 (四舍五入到 Ω 位有效数字)
   - k 为余数系数 (k = (a/b - M) / x)
3. 余数永存: k 永远不为 0 (除非 a 能被 b 整除)
4. 运算前必须统一 Ω (精度对齐) 和分母 (通分)

作者: 刘一京 (Yijing Liu)
许可: MIT License
"""

from decimal import Decimal, getcontext
from math import gcd
from typing import Union

# 设置 Decimal 全局精度 (足够覆盖 Ω≤35 的所有场景)
getcontext().prec = 120


class DDHNumber:
    """
    DDH-Float 核心数据类型
    表示一个带显式余数的有理数: value = M + k·x
    """

    # ------------------------------------------------------------------
    # 构造与初始化
    # ------------------------------------------------------------------
    def __init__(self, numerator: int, denominator: int, omega: int,
                 strict_mode: bool = True):
        """
        Parameters
        ----------
        numerator : int
            分子 a
        denominator : int
            分母 b (除数标签), 不能为 0
        omega : int
            精度参数 Ω, x = 1/10^Ω, 必须为正整数
        strict_mode : bool
            True  -> 严格模式, 始终显示余部 k·x
            False -> 兼容模式, 余部为 0 时省略
        """
        if denominator == 0:
            raise ZeroDivisionError("DDHNumber: 除数 (分母 b) 不能为 0")
        if omega <= 0:
            raise ValueError(f"DDHNumber: 精度 Ω 必须为正整数, 当前为 {omega}")
        if not isinstance(numerator, int):
            raise TypeError(f"DDHNumber: 分子必须为整数, 当前为 {type(numerator)}")
        if not isinstance(denominator, int):
            raise TypeError(f"DDHNumber: 分母必须为整数, 当前为 {type(denominator)}")
        if not isinstance(omega, int):
            raise TypeError(f"DDHNumber: Ω 必须为整数, 当前为 {type(omega)}")

        self.a: int = numerator
        self.b: int = denominator
        self.omega: int = omega
        self.strict: bool = strict_mode

        # 最小不可分单位
        self.x: Decimal = Decimal(1) / (Decimal(10) ** omega)

        # 真实值 (高精度 Decimal)
        self.exact: Decimal = Decimal(numerator) / Decimal(denominator)

        # 主部 M: 四舍五入到 Ω 位小数
        quantize_str = "0." + "0" * omega
        self.M: Decimal = self.exact.quantize(Decimal(quantize_str))

        # 余数系数 k = (真实值 - 主部) / x
        residual = self.exact - self.M
        self.k: Decimal = residual / self.x

        # 进位处理: 若 |k| >= 1, 将整数部分进位到主部
        self._carry()

        # 清理尾零
        self.M = self.M.normalize()

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------
    def _carry(self) -> None:
        """若 |k| >= 1, 将整数部分进位到主部 M"""
        if abs(self.k) >= 1:
            carry = int(self.k)
            self.M += Decimal(carry) * self.x
            self.k -= Decimal(carry)
            self.M = self.M.normalize()

    def _align_omega(self, other: "DDHNumber") -> None:
        """检查 Ω 是否一致, 不一致则抛出异常"""
        if self.omega != other.omega:
            raise ValueError(
                f"DDHNumber: Ω 不匹配 ({self.omega} ≠ {other.omega}), "
                f"请先统一精度 Ω"
            )

    def _value(self) -> Decimal:
        """返回完整精确值 M + k·x"""
        return self.M + self.k * self.x

    # ------------------------------------------------------------------
    # 算术运算
    # ------------------------------------------------------------------
    def __add__(self, other: "DDHNumber") -> "DDHNumber":
        """加法: 统一分母 (LCM 通分) 后相加"""
        if not isinstance(other, DDHNumber):
            raise TypeError(f"DDHNumber: 不支持与 {type(other)} 相加")
        self._align_omega(other)

        lcm_d = self.b * other.b // gcd(self.b, other.b)
        new_a = self.a * (lcm_d // self.b) + other.a * (lcm_d // other.b)
        return DDHNumber(new_a, lcm_d, self.omega, self.strict)

    def __sub__(self, other: "DDHNumber") -> "DDHNumber":
        """减法: 加上负数"""
        neg_other = DDHNumber(-other.a, other.b, other.omega, other.strict)
        return self + neg_other

    def __mul__(self, other: "DDHNumber") -> "DDHNumber":
        """乘法: 嵌套分割 (a/b)*(c/d) = (ac)/(bd)"""
        if not isinstance(other, DDHNumber):
            raise TypeError(f"DDHNumber: 不支持与 {type(other)} 相乘")
        self._align_omega(other)
        return DDHNumber(self.a * other.a, self.b * other.b,
                         self.omega, self.strict)

    def __truediv__(self, other: "DDHNumber") -> "DDHNumber":
        """除法: 乘以倒数 (a/b)/(c/d) = (ad)/(bc)"""
        if not isinstance(other, DDHNumber):
            raise TypeError(f"DDHNumber: 不支持与 {type(other)} 相除")
        if other.a == 0:
            raise ZeroDivisionError("DDHNumber: 除数不能为 0")
        self._align_omega(other)
        return DDHNumber(self.a * other.b, self.b * other.a,
                         self.omega, self.strict)

    def __neg__(self) -> "DDHNumber":
        """取负"""
        return DDHNumber(-self.a, self.b, self.omega, self.strict)

    def __abs__(self) -> "DDHNumber":
        """绝对值"""
        return DDHNumber(abs(self.a), self.b, self.omega, self.strict)

    # ------------------------------------------------------------------
    # 比较运算
    # ------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DDHNumber):
            return NotImplemented
        return self._value() == other._value()

    def __lt__(self, other: "DDHNumber") -> bool:
        if not isinstance(other, DDHNumber):
            raise TypeError(f"DDHNumber: 不支持与 {type(other)} 比较")
        self._align_omega(other)
        return self._value() < other._value()

    def __le__(self, other: "DDHNumber") -> bool:
        return self < other or self == other

    def __gt__(self, other: "DDHNumber") -> bool:
        if not isinstance(other, DDHNumber):
            raise TypeError(f"DDHNumber: 不支持与 {type(other)} 比较")
        self._align_omega(other)
        return self._value() > other._value()

    def __ge__(self, other: "DDHNumber") -> bool:
        return self > other or self == other

    # ------------------------------------------------------------------
    # 类型转换
    # ------------------------------------------------------------------
    def to_float(self) -> float:
        """返回标准浮点近似值"""
        return float(self._value())

    def to_decimal(self) -> Decimal:
        """返回精确 Decimal 值"""
        return self._value()

    # ------------------------------------------------------------------
    # 字符串表示
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        m_str = f"{self.M}"

        if self.strict:
            if self.k == 0:
                return f"{self.a}/{self.b} = {m_str} (Ω={self.omega}, 整除)"
            k_float = float(self.k)
            if abs(k_float) < 1e-6 or abs(k_float) >= 1e6:
                k_str = f"{k_float:.6e}"
            else:
                k_str = f"{k_float:.10f}".rstrip("0").rstrip(".")
                if k_str == "-0":
                    k_str = "0"
            return f"{self.a}/{self.b} = {m_str} + {k_str}x (Ω={self.omega})"
        else:
            if self.k == 0:
                return f"{self.a}/{self.b} = {m_str}"
            k_float = float(self.k)
            k_str = f"{k_float:.10f}".rstrip("0").rstrip(".")
            return f"{self.a}/{self.b} = {m_str} + {k_str}x"

    # ------------------------------------------------------------------
    # 类方法: 便捷构造
    # ------------------------------------------------------------------
    @classmethod
    def from_float(cls, value: float, omega: int,
                   strict_mode: bool = True) -> "DDHNumber":
        """从浮点数构造 (近似)"""
        from fractions import Fraction
        frac = Fraction(value).limit_denominator(10**omega)
        return cls(frac.numerator, frac.denominator, omega, strict_mode)

    @classmethod
    def zero(cls, omega: int, strict_mode: bool = True) -> "DDHNumber":
        """返回 DDH 零值"""
        return cls(0, 1, omega, strict_mode)

    @classmethod
    def one(cls, omega: int, strict_mode: bool = True) -> "DDHNumber":
        """返回 DDH 单位元 1"""
        return cls(1, 1, omega, strict_mode)
