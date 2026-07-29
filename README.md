# RED-ARITH: Tagged-Residue Floating-Point Arithmetic

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**REliable Deterministic Arithmetic for High-Stakes Computing**

RED-ARITH introduces a novel tagged-residue floating-point representation designed to eliminate the non-determinism and hidden errors inherent in standard floating-point operations. By explicitly tracking the residue label (k) and denominator (D) alongside the main value (M), this library ensures bit-for-bit reproducible results across diverse hardware platforms.

## 💡 Core Innovation

Traditional floating-point math can produce subtle variations due to compiler optimizations or hardware differences. RED-ARITH solves this by:
*   **Deterministic Scaling**: Residue scaling during arithmetic operations guarantees consistent outcomes.
*   **Audit-Friendly**: Every number carries its own mathematical context, making debugging and verification straightforward.
*   **Zero Error Tolerance**: Ideal for applications where numerical fidelity is non-negotiable.

## 🚀 Getting Started

*(这里根据你的实际情况填写，如果是C++/Python库，写上编译命令；如果是论文附属代码，可以写如何使用)*

## 📜 Citation

If you use RED-ARITH in your research or project, please cite our work:
