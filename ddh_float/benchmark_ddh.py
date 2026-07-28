"""
benchmark_ddh.py
==================
DDH-Float vs IEEE 754 浮点 性能与精度基准测试

运行方式:
    python benchmark_ddh.py
"""

import time
import sys

# 导入 DDHNumber
try:
    from ddh_float import DDHNumber
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ddh_float_mod", "ddh_float.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    DDHNumber = mod.DDHNumber


def timeit(func, iterations=10000):
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed = time.perf_counter() - start
    per_call = (elapsed / iterations) * 1e6
    return elapsed, per_call


# ======================================================================
# 测试 1: 单值精度对比
# ======================================================================
def benchmark_precision():
    print("\n" + "=" * 72)
    print("测试 1: 单值精度对比 (Ω=16)")
    print("=" * 72)
    header = f"{'数值':<12} {'标准浮点':<22} {'DDH值':<22} {'差值':<18}"
    print(header)
    print("-" * 72)

    omega = 16
    cases = [
        (1, 3, "1/3"),
        (1, 7, "1/7"),
        (22, 7, "22/7"),
        (1, 2, "1/2"),
        (3, 8, "3/8"),
        (5, 9, "5/9"),
        (355, 113, "355/113"),
    ]

    for a, b, name in cases:
        std = a / b
        ddh = DDHNumber(a, b, omega)
        ddh_val = ddh.to_float()
        diff = ddh_val - std
        print(f"{name:<12} {std:<22.16f} {ddh_val:<22.16f} {diff:<18.2e}")


# ======================================================================
# 测试 2: 累积误差
# ======================================================================
def benchmark_cumulative():
    print("\n" + "=" * 72)
    print("测试 2: 累积误差 (加 N 次 0.1)")
    print("=" * 72)

    omega = 16
    header = (f"{'N':<10} {'标准浮点':<22} {'标准误差':<18} "
              f"{'DDH':<22} {'DDH误差':<18}")
    print(header)
    print("-" * 72)

    for N in [100, 1000, 10000, 100000]:
        # 标准浮点
        s = 0.0
        for _ in range(N):
            s += 0.1
        fe = abs(s - N * 0.1)

        # DDH
        d = DDHNumber(0, 1, omega)
        t = DDHNumber(1, 10, omega)
        for _ in range(N):
            d = d + t
        dv = d.to_float()
        de = abs(dv - N * 0.1)

        print(f"{N:<10} {s:<22.13f} {fe:<18.2e} {dv:<22.13f} {de:<18.2e}")

    # 耗时对比
    print("\n--- 10万次累加耗时 ---")
    N = 100000

    def fl():
        s = 0.0
        for i in range(N):
            s += 0.1
        return s

    def dl():
        s = DDHNumber(0, 1, omega)
        t = DDHNumber(1, 10, omega)
        for i in range(N):
            s = s + t
        return s

    _, fu = timeit(fl, 5)
    _, du = timeit(dl, 5)

    print(f"  标准浮点: {fu:.1f} μs/call")
    print(f"  DDH:      {du:.1f} μs/call")
    print(f"  比值:     DDH 慢 {du/fu:.1f}x (软件模拟预期)")


# ======================================================================
# 测试 3: 封闭性验证
# ======================================================================
def benchmark_closure():
    print("\n" + "=" * 72)
    print("测试 3: 有理数运算封闭性验证")
    print("=" * 72)

    omega = 16
    tests = [
        ("1/3+1/3+1/3", (1,3), (1,3), (1,3), "add3"),
        ("1/2+1/2",     (1,2), (1,2), None,  "add2"),
        ("2/3-1/3",     (2,3), (1,3), None,  "sub"),
        ("1/2×1/2",     (1,2), (1,2), None,  "mul"),
        ("1/2÷1/4",     (1,2), (1,4), None,  "div"),
        ("3/4×2/3",     (3,4), (2,3), None,  "mul"),
    ]

    print(f"{'运算':<16} {'结果':<20} {'预期':<20} {'误差':<12} {'余部k'}")
    print("-" * 72)

    for name, p1, p2, p3, op in tests:
        a1, b1 = p1
        a2, b2 = p2
        x1 = DDHNumber(a1, b1, omega)
        x2 = DDHNumber(a2, b2, omega)

        if op == "add3" and p3:
            a3, b3 = p3
            x3 = DDHNumber(a3, b3, omega)
            r = x1 + x2 + x3
            exp = a1/b1 + a2/b2 + a3/b3
        elif op == "add2":
            r = x1 + x2
            exp = a1/b1 + a2/b2
        elif op == "sub":
            r = x1 - x2
            exp = a1/b1 - a2/b2
        elif op == "mul":
            r = x1 * x2
            exp = (a1/b1) * (a2/b2)
        elif op == "div":
            r = x1 / x2
            exp = (a1/b1) / (a2/b2)

        val = r.to_float()
        err = abs(val - exp)
        ks = f"{float(r.k):.6f}" if r.k != 0 else "0"
        print(f"{name:<16} {val:<20.10f} {exp:<20.10f} {err:<12.2e} {ks}")


# ======================================================================
# 测试 4: Ω 可调性
# ======================================================================
def benchmark_omega():
    print("\n" + "=" * 72)
    print("测试 4: Ω 精度可调性")
    print("=" * 72)

    print(f"{'Ω':<6} {'1/2 主部':<22} {'1/2 余部k':<18} {'1/3 余部k':<18}")
    print("-" * 72)

    for omega in [1, 2, 4, 8, 16, 32]:
        half = DDHNumber(1, 2, omega)
        third = DDHNumber(1, 3, omega)
        hk = float(half.k)
        tk = float(third.k)
        print(f"{omega:<6} {float(half.M):<22.10f} {hk:<18.6f} {tk:<18.6f}")


# ======================================================================
# 测试 5: 误差可见性
# ======================================================================
def benchmark_visibility():
    print("\n" + "=" * 72)
    print("测试 5: 误差可见性 (DDH 独有优势)")
    print("=" * 72)

    omega = 16
    x = 1e-16

    print(f"{'数值':<10} {'标准浮点':<22} {'DDH主部':<22} {'DDH余部kx':<20}")
    print("-" * 72)

    for a, b, name in [(1,7,"1/7"), (22,7,"22/7"), (1,3,"1/3"), (5,9,"5/9")]:
        sv = a / b
        d = DDHNumber(a, b, omega)
        res = float(d.k) * x
        print(f"{name:<10} {sv:<22.16f} {float(d.M):<22.16f} {res:<20.2e}")


# ======================================================================
# 主入口
# ======================================================================
if __name__ == "__main__":
    print("DDH-Float vs IEEE 754 浮点")
    print("性能与精度基准测试 v1.0")
    print(f"Python: {sys.version.split()[0]}")

    benchmark_precision()
    benchmark_cumulative()
    benchmark_closure()
    benchmark_omega()
    benchmark_visibility()

    print("\n" + "=" * 72)
    print("基准测试完成")
    print("=" * 72)
