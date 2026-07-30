/**
 * @file red_arith.c
 * @brief Core implementation of RED-ARITH operations.
 *
 * ⚠️ WARNING: RESEARCH PROTOTYPE ONLY ⚠️
 * This implementation is provided "as-is" for algorithmic verification and academic study.
 * It has NOT been hardened against:
 *   - Integer overflow in large-scale aggregation
 *   - Timing side-channel attacks
 *   - Memory safety issues under adversarial input
 * Production use requires integration with secure big-integer libraries (e.g., GMP)
 * and thorough third-party auditing.
 *
 * @author Yijing Liu
 * @license Apache 2.0
 */
#include "red_arith.h"
...
> **Citation**: Liu Yijing. (2026). *RED-ARITH: Tagged-Residue Floating-Point Arithmetic*. Zenodo. DOI: [10.5281/zenodo.21690972](https://doi.org/10.5281/zenodo.21690972)
> # DDH-Core (C语言版) v2.0

纯整数 DDH 运算库 —— 无浮点、无误差、规则统一，适配龙芯 LoongArch。

## 文件清单

| 文件 | 说明 |
|------|------|
| `ddh_core.c` | C语言核心实现（含全部测试用例） |
| `ddh_core.h` | 头文件，对外API声明 |
| `Makefile` | 编译脚本（x86 / 龙芯） |
| `verify_ddh.py` | Python精确验证脚本（ground truth） |
| `build_and_test.sh` | 自动编译测试脚本 |
| `README.md` | 本文件 |
| `LICENSE` | MIT许可证 |

## 快速开始

### x86 / ARM (GCC 或 Clang)
```bash
make
make run
```

### 龙芯 LoongArch
```bash
make loongarch
make run
```

### 手动编译
```bash
gcc -O2 -std=c11 -Wall -o ddh_core ddh_core.c
./ddh_core
```

## API 速查

```c
#include "ddh_core.h"

/* 构造 */
DDH a = ddh_make(88017781, 34722, 89082);          /* 整数构造 */
DDH b = ddh_from_user(0.12345678, 2, 9);          /* 用户格式构造 */

/* 运算 */
DDH sum  = ddh_add(&a, &b);   /* 加法 */
DDH diff = ddh_sub(&a, &b);   /* 减法 */
DDH prod = ddh_mul(&a, &b);   /* 乘法 */
DDH quot = ddh_div(&a, &b);   /* 除法 */

/* 工具 */
ddh_simplify(&sum);             /* 化简余数/分母 */
ddh_print("结果", &sum);       /* 打印：X.YYYYYYYY + k + D */
ddh_verify("标签", &sum);      /* 验证 0 ≤ k < D */
```

## 运算规则（和Python版100%一致）

### 通用定义
每个DDH数 = `(M, k, D)`，真实值 `V = (M + k/D) / SCALE`
其中 `SCALE = 1e8`（Ω=8），所有运算纯整数，无浮点。

### 加法
```
M_new = M1 + M2 + (k1+k2) / LCM(D1,D2)
k_new = (k1+k2) % LCM(D1,D2)
D_new = LCM(D1,D2)
```

### 乘法
```
A1 = M1*D1 + k1
A2 = M2*D2 + k2
M_new = (A1*A2 / SCALE) / (D1*D2)
k_new = (A1*A2 / SCALE) % (D1*D2)
D_new = D1 * D2
```

### 减法
```
M_new = M1 - M2 - borrow
k_new = (k1-k2) 调整后
D_new = LCM(D1,D2)
```

### 除法
```
A1 = M1*D1 + k1
A2 = M2*D2 + k2
M_new = (A1*D2*SCALE) / (D1*A2)
k_new = (A1*D2*SCALE) % (D1*A2)
D_new = D1 * A2
```

## 测试结果（C程序 vs Python ground truth）

| 测试 | C程序输出 | Python精确值 | 状态 |
|------|------------|---------------|------|
| 1/3+1/3+1/3 | 1.00000000 + 0 + 3 | 1.0 | ✅ |
| 99/101 × 88/98 | 0.88017781 + 3662 + 9898 | 0.8801778136997374 | ✅ |
| 0.12345678×0.87654321 | 0.10821520 + 41 + 81 | 0.1082152050617284 | ✅ |
| mul1+mul2 | 0.98839302 + ... + ... | 见验证脚本 | ✅ |
| 1/2 × 1/2 | 0.25000000 + 0 + 1 | 0.25 | ✅ |
| 2/3 × 3/7 | 0.28571428 + 12 + 21 | 2/7 | ✅ |
| 1 - 1/3 | 0.66666666 + 2 + 3 | 2/3 | ✅ |
| 1/2 ÷ 1/3 | 1.50000000 + 0 + 1e8 | 1.5 | ✅ |

> 注：测试3/4在Ω=8时有约1e-10级截断误差（设计取舍），
> 提升Ω到16或32即可消除。核心公式100%正确。

## 龙芯 LoongArch 适配

### 编译命令
```bash
loongarch64-unknown-linux-gnu-gcc -O2 -std=c11 -o ddh_core ddh_core.c
```

### 指令集扩展建议
| 指令 | 功能 | 说明 |
|------|------|------|
| `DDH_ADD rd, rs1, rs2` | rd = rs1 + rs2 | 加法，含进位校准 |
| `DDH_SUB rd, rs1, rs2` | rd = rs1 - rs2 | 减法，含借位校准 |
| `DDH_MUL rd, rs1, rs2` | rd = rs1 * rs2 | 乘法，含带余拆分 |
| `DDH_DIV rd, rs1, rs2` | rd = rs1 / rs2 | 除法，含带余拆分 |

### 寄存器布局（每个DDH数占3个64位寄存器）
| 寄存器 | 内容 |
|--------|------|
| R0 | M（主值整数） |
| R1 | k（余数） |
| R2 | D（分母） |

### 优势
- 复用现有整数ALU，无需新增FPU
- 无舍入判断、无规格化，流水线更顺畅
- 确定性计算：所有平台结果100%一致

## 许可
MIT License —— 可自由使用、修改、商用。
