"""
test_ddh_float.py
==================
DDH-Float 单元测试套件

运行方式:
    python -m pytest test_ddh_float.py -v
    或
    python test_ddh_float.py
"""

import sys
import time
import math

# 优先从包导入, 失败则从单文件导入
try:
    from ddh_float import DDHNumber
except ImportError:
    # 兼容旧结构: 直接跑 ddh_float.py
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ddh_float_mod", "ddh_float.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    DDHNumber = mod.DDHNumber


def _assert_close(ddh_val, expected, tol=1e-12, msg=""):
    diff = abs(ddh_val - expected)
    assert diff < tol, f"{msg}: 期望 {expected}, 实际 {ddh_val}, 差 {diff}"


# ======================================================================
# 1. 构造与异常
# ======================================================================
class TestConstruction:
    def test_omega_must_be_positive(self):
        try:
            DDHNumber(1, 2, 0)
            assert False, "应抛出 ValueError"
        except ValueError:
            pass
        try:
            DDHNumber(1, 2, -1)
            assert False, "应抛出 ValueError"
        except ValueError:
            pass

    def test_denominator_cannot_be_zero(self):
        try:
            DDHNumber(1, 0, 8)
            assert False, "应抛出 ZeroDivisionError"
        except ZeroDivisionError:
            pass

    def test_non_integer_inputs(self):
        try:
            DDHNumber(1.5, 2, 8)
            assert False, "应抛出 TypeError"
        except TypeError:
            pass

    def test_basic_fractions(self):
        omega = 16
        half = DDHNumber(1, 2, omega)
        assert half.a == 1 and half.b == 2
        assert half.omega == omega
        third = DDHNumber(1, 3, omega)
        assert third.a == 1 and third.b == 3


# ======================================================================
# 2. 核心公理验证
# ======================================================================
class TestAxioms:
    def test_axiom_unit(self):
        """
        单位元验证 (Ω=8)
        1 = 1.00000000, 整除时余部 k=0 (M已精确等于1)
        这是正确行为: 当 a%b==0 时, DDH 精确表示, 无需余部
        """
        omega = 8
        one = DDHNumber(1, 1, omega, strict_mode=True)
        # 完整值应精确等于 1
        _assert_close(one.to_float(), 1.0, tol=1e-15, msg="1 完整值")
        # 整除时 k=0 (正确行为)
        assert one.k == 0, f"1 应整除, k={one.k}"
        # 字符串应显示 "整除"
        assert "整除" in str(one), f"应显示整除: {one}"

    def test_axiom_half(self):
        """1/2 = 0.49999999 + 1·x (Ω=8)"""
        omega = 8
        half = DDHNumber(1, 2, omega, strict_mode=True)
        _assert_close(half.to_float(), 0.5, tol=1e-15, msg="1/2")

    def test_axiom_third(self):
        """1/3 验证: 完整值等于 1/3"""
        omega = 16
        third = DDHNumber(1, 3, omega)
        _assert_close(third.to_float(), 1/3, tol=1e-14, msg="1/3")

    def test_axiom_fourth(self):
        """1/4 验证"""
        omega = 8
        fourth = DDHNumber(1, 4, omega)
        _assert_close(fourth.to_float(), 0.25, tol=1e-15, msg="1/4")

    def test_axiom_fifth(self):
        """1/5 验证"""
        omega = 8
        fifth = DDHNumber(1, 5, omega)
        _assert_close(fifth.to_float(), 0.2, tol=1e-15, msg="1/5")

    def test_axiom_seven(self):
        """1/7 验证"""
        omega = 16
        sev = DDHNumber(1, 7, omega)
        _assert_close(sev.to_float(), 1/7, tol=1e-14, msg="1/7")


# ======================================================================
# 3. 四则运算封闭性
# ======================================================================
class TestArithmetic:
    def test_add_thirds(self):
        """1/3 + 1/3 + 1/3 = 1"""
        omega = 16
        third = DDHNumber(1, 3, omega)
        result = third + third + third
        _assert_close(result.to_float(), 1.0, tol=1e-13, msg="3*(1/3)")

    def test_mul_half(self):
        """1/2 * 1/2 = 1/4"""
        omega = 16
        half = DDHNumber(1, 2, omega)
        result = half * half
        _assert_close(result.to_float(), 0.25, tol=1e-14, msg="1/2*1/2")

    def test_div_half(self):
        """1/2 ÷ 1/4 = 2"""
        omega = 16
        half = DDHNumber(1, 2, omega)
        quarter = DDHNumber(1, 4, omega)
        result = half / quarter
        _assert_close(result.to_float(), 2.0, tol=1e-13, msg="1/2÷1/4")

    def test_sub_thirds(self):
        """2/3 - 1/3 = 1/3"""
        omega = 16
        two = DDHNumber(2, 3, omega)
        one = DDHNumber(1, 3, omega)
        result = two - one
        _assert_close(result.to_float(), 1/3, tol=1e-14, msg="2/3-1/3")

    def test_add_half_half(self):
        """1/2 + 1/2 = 1"""
        omega = 16
        half = DDHNumber(1, 2, omega)
        result = half + half
        _assert_close(result.to_float(), 1.0, tol=1e-14, msg="1/2+1/2")

    def test_negation(self):
        """-1/3 + 1/3 = 0"""
        omega = 16
        third = DDHNumber(1, 3, omega)
        neg = -third
        result = third + neg
        _assert_close(result.to_float(), 0.0, tol=1e-14, msg="取负")

    def test_omega_mismatch_add(self):
        """不同 Ω 不能相加"""
        a = DDHNumber(1, 2, 8)
        b = DDHNumber(1, 2, 16)
        try:
            a + b
            assert False, "应抛出 ValueError"
        except ValueError:
            pass

    def test_division_by_zero(self):
        """除以零应报错"""
        omega = 8
        one = DDHNumber(1, 1, omega)
        zero = DDHNumber(0, 1, omega)
        try:
            one / zero
            assert False, "应抛出 ZeroDivisionError"
        except ZeroDivisionError:
            pass


# ======================================================================
# 4. 精度可调性
# ======================================================================
class TestPrecision:
    def test_omega_variability(self):
        """Ω 为任意正整数"""
        for omega in [1, 4, 8, 16, 32]:
            half = DDHNumber(1, 2, omega)
            _assert_close(half.to_float(), 0.5, tol=1e-10, msg=f"Ω={omega}")

    def test_large_omega(self):
        """Ω=35 (普朗克尺度)"""
        omega = 35
        half = DDHNumber(1, 2, omega)
        _assert_close(half.to_float(), 0.5, tol=1e-30, msg=f"Ω={omega}")

    def test_omega_1_edge_case(self):
        """Ω=1 边界"""
        omega = 1
        half = DDHNumber(1, 2, omega)
        _assert_close(half.to_float(), 0.5, tol=1e-6, msg="Ω=1")


# ======================================================================
# 5. 与标准浮点对比
# ======================================================================
class TestVsFloat:
    def test_1000_sum_0_1(self):
        """加 1000 次 0.1"""
        omega = 16
        float_sum = 0.0
        for _ in range(1000):
            float_sum += 0.1
        float_error = abs(float_sum - 100.0)

        ddh_sum = DDHNumber(0, 1, omega)
        for _ in range(1000):
            ddh_sum = ddh_sum + DDHNumber(1, 10, omega)
        ddh_val = ddh_sum.to_float()
        ddh_error = abs(ddh_val - 100.0)

        assert float_error < 1e-11
        assert ddh_error < 1e-11

    def test_fraction_closure(self):
        """有理数运算无精度损失"""
        omega = 16
        sev = DDHNumber(1, 7, omega)
        result = sev * DDHNumber(7, 1, omega)
        _assert_close(result.to_float(), 1.0, tol=1e-13, msg="7*(1/7)")

    def test_determinism(self):
        """运算确定性"""
        omega = 16
        results = []
        for _ in range(100):
            a = DDHNumber(1, 3, omega)
            b = DDHNumber(1, 3, omega)
            c = a + b
            results.append(c.to_float())
        assert all(r == results[0] for r in results)


# ======================================================================
# 6. 比较运算
# ======================================================================
class TestComparison:
    def test_less_than(self):
        omega = 8
        half = DDHNumber(1, 2, omega)
        third = DDHNumber(1, 3, omega)
        assert third < half
        assert half > third

    def test_omega_mismatch_comp(self):
        a = DDHNumber(1, 2, 8)
        b = DDHNumber(1, 2, 16)
        try:
            a < b
            assert False, "应抛出 ValueError"
        except ValueError:
            pass


# ======================================================================
# 7. 边界与异常
# ======================================================================
class TestEdgeCases:
    def test_zero(self):
        omega = 8
        zero = DDHNumber(0, 1, omega)
        assert zero.to_float() == 0.0

    def test_negative(self):
        omega = 8
        neg = DDHNumber(-1, 2, omega)
        _assert_close(neg.to_float(), -0.5, tol=1e-15)

    def test_strict_vs_compat(self):
        omega = 8
        strict = DDHNumber(1, 1, omega, strict_mode=True)
        compat = DDHNumber(1, 1, omega, strict_mode=False)
        assert strict.to_float() == compat.to_float()
        s = str(strict)
        c = str(compat)
        # 兼容模式整除不含 "x"
        assert "x" not in c or "0x" in c.lower()


# ======================================================================
# 主入口
# ======================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("DDH-Float 单元测试套件 v1.0")
    print("=" * 70)

    test_classes = [
        TestConstruction, TestAxioms, TestArithmetic,
        TestPrecision, TestVsFloat, TestComparison, TestEdgeCases,
    ]

    total_passed = 0
    total_failed = 0
    total_time = 0.0

    for cls in test_classes:
        print(f"\n--- {cls.__name__} ---")
        passed = 0
        failed = 0
        start = time.time()

        for method_name in dir(cls):
            if method_name.startswith("test_"):
                try:
                    method = getattr(cls(), method_name)
                    method()
                    print(f"  ✓ {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"  ✗ {method_name}: {type(e).__name__}: {e}")
                    failed += 1

        elapsed = time.time() - start
        total_time += elapsed
        print(f"  ({passed} passed, {failed} failed, {elapsed:.3f}s)")
        total_passed += passed
        total_failed += failed

    print("\n" + "=" * 70)
    print(f"总计: {total_passed} 通过, {total_failed} 失败, "
          f"{total_time:.3f} 秒")
    print("=" * 70)

    if total_failed > 0:
        sys.exit(1)
