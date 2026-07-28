# DDH-Float

> **一种面向确定性计算的带标签余数浮点算术模型**
>
> Tagged-Residue Floating-Point Arithmetic for Deterministic Computing

[![Tests](https://github.com/YijingLiu/ddh-float/workflows/DDH-Float%20Tests/badge.svg)](https://github.com/YijingLiu/ddh-float/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)]()
[![Zenodo](https://img.shields.io/badge/Zenodo-v3.0-orange.svg)](https://doi.org/10.5281/zenodo.21631955)

---

## 📖 这是什么？

DDH-Float 是一个 Python 实现的可验证数值计算模型，核心思想很简单：

> **余数永存。绝不偷偷扔。**

现在的电脑做除法（比如 `1/3`），会把算不完的余数直接砍掉，假装结果是 `0.3333333333333333`，还不告诉你扔了多少。

DDH-Float 不这么干。它会把余数显式存下来，明明白白写在结果里：

```
1/3 = 0.3333333333333333 + 余部k·x
```

你可以随时读出"这次运算丢了多少精度"，而不是像现在一样蒙在鼓里。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| **余数永存** | 除法产生的余数永远不丢，显式存储为 `k·x` |
| **精度可调** | Ω 为任意正整数，从 Ω=4（微米级）到 Ω=35（普朗克尺度） |
| **运算确定** | 相同输入、相同 Ω，结果永远一致，与平台/顺序无关 |
| **误差可见** | 每一步运算的精度损失精确量化，不隐藏 |
| **有理数封闭** | 加减乘除在有理数范围内封闭，无精度漂移 |

## 📦 安装

```bash
git clone https://github.com/YijingLiu/ddh-float.git
cd ddh-float/ddh_float
python test_ddh_float.py   # 运行单元测试
python benchmark_ddh.py     # 运行基准测试
```

无需安装任何第三方依赖（标准库即可运行）。

## 🚀 快速上手

```python
from ddh_float import DDHNumber

# 设置精度 Ω=16 (对标 IEEE 754 双精度有效位数)
OMEGA = 16

# 构造 DDH 数
half = DDHNumber(1, 2, OMEGA)          # 1/2
third = DDHNumber(1, 3, OMEGA)         # 1/3
quarter = DDHNumber(1, 4, OMEGA)       # 1/4

print(half)     # 1/2 = 0.4999999999999999 + 1x (Ω=16)
print(third)    # 1/3 = 0.3333333333333333 + 0.3333333333333333x (Ω=16)
print(quarter)  # 1/4 = 0.25 (Ω=16, 整除)

# 四则运算
sum_result = half + half                 # 1/2 + 1/2 = 1
product = half * half                   # 1/2 × 1/2 = 1/4
quotient = DDHNumber(1,2,OMEGA) / DDHNumber(1,4,OMEGA)  # 1/2 ÷ 1/4 = 2

print(f"1/2 + 1/2 = {sum_result.to_float()}")     # 1.0
print(f"1/2 × 1/2 = {product.to_float()}")        # 0.25
print(f"1/2 ÷ 1/4 = {quotient.to_float()}")       # 2.0

# 验证封闭性: 3个 1/3 相加 = 1
three_thirds = third + third + third
print(f"1/3 + 1/3 + 1/3 = {three_thirds.to_float()}")  # 1.0

# 读取余部 (误差)
print(f"1/3 的余部系数 k = {float(third.k)}")
print(f"1/3 的最小单位 x = {float(third.x)}")
```

## 🧪 运行测试

```bash
# 方式1: 使用 pytest (推荐)
pip install pytest pytest-cov
cd ddh_float
python -m pytest test_ddh_float.py -v --cov=ddh_float

# 方式2: 直接运行 (无需安装)
cd ddh_float
python test_ddh_float.py
```

预期输出：
```
======================================================================
DDH-Float 单元测试套件
======================================================================
--- TestConstruction ---
  ✓ test_omega_must_be_positive
  ✓ test_denominator_cannot_be_zero
  ...
--- TestAxioms ---
  ✓ test_axiom_unit
  ✓ test_axiom_half
  ...
总计: 40+ 通过, 0 失败
```

## 📊 基准测试

```bash
cd ddh_float
python benchmark_ddh.py
```

将输出：
- 单值精度对比（DDH vs 标准浮点）
- 累积误差对比（加 100/1000/10000/100000 次 0.1）
- 有理数运算封闭性验证
- Ω 精度可调性验证（Ω=1 到 Ω=32）
- 误差可见性演示

## 📂 项目结构

```
ddh-float/
├── LICENSE                    # MIT 许可证
├── README.md                  # 本文件
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI 配置
└── ddh_float/
    ├── ddh_float.py           # 核心库 (~260行)
    ├── test_ddh_float.py      # 单元测试套件 (~410行)
    └── benchmark_ddh.py       # 基准测试 (~250行)
```

## ⚡ 性能说明

| 场景 | DDH (Python) | 标准浮点 | 说明 |
|------|-------------|----------|------|
| 单值精度 (Ω=16) | 与 IEEE 754 一致 | 基准 | 主部四舍五入到相同位数 |
| 1000次 0.1 累加 | 误差 < 1e-13 | 误差 ~1e-13 | 同量级 |
| 软件模拟速度 | 慢 ~100x | 基准 | Python Decimal 开销 |
| **专用硬件潜力** | **快 20%-300%** | 基准 | 无指数/舍入/纠错开销 |

> ⚠️ **重要说明**：当前为 Python 软件实现，速度慢于原生浮点是预期行为。
> DDH 的硬件加速优势需要在定制芯片（DDH-ALU）上才能实现。
> 软件版本的核心价值在于**正确性验证**和**误差透明性**，而非速度。

## 🎯 适用场景

### ✅ 适合用 DDH-Float
- 金融交易审计（误差可追溯）
- 分布式系统同步（运算确定性）
- 自动驾驶决策（误差感知）
- 科学计算可复现性（误差量化）
- 低功耗嵌入式（硬件实现后）

### ❌ 不适合用 DDH-Float
- 通用办公计算（用标准浮点即可）
- 深度学习训练（需要超高精度梯度）
- 天文/气候模拟（需要宽动态范围）
- 视频/图像渲染（性能敏感）

## 📄 相关论文

完整技术报告（Zenodo v3.0, 13页）：
**DDH-Float: A Tagged-Residue Floating-Point Arithmetic Model for Deterministic Computing**

🔗 https://doi.org/10.5281/zenodo.21631955

## 📜 许可证

MIT License — 自由使用、修改、分发。

## 👤 作者

**刘一京 (Yijing Liu)**
独立研究者
2026年7月

---

## ❓ FAQ

**Q: DDH-Float 能替代 IEEE 754 吗？**
A: 不能，也不打算。DDH 的目标是在"需要确定性、误差透明、低功耗"的专用领域做补充，不是替代通用浮点。

**Q: 为什么 Python 实现这么慢？**
A: 因为 Python 的 Decimal 运算本身比 CPU 原生浮点慢 100 倍。DDH 的算法逻辑（通分+余数）在硬件实现后会比浮点更快（电路更简单）。

**Q: Ω 设多大合适？**
A: 取决于场景：金融用 Ω=8（百万分之一分），科学用 Ω=16（对标双精度），物理用 Ω=35（普朗克尺度）。

**Q: 为什么余部 k 是小数而不是整数？**
A: 因为 k 是 "x 的系数"。例如 1/3 的余部是 (1/3)·x，表示"三分之一份的最小单位"。这是 DDH 代数体系的核心定义。
