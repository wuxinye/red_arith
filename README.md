# RED-ARITH

> **⚠️ Research Prototype Warning**
> This codebase is a **research prototype** intended for algorithmic verification and academic study.
> **It is NOT production-ready.** Do not deploy this code in financial production systems, audit pipelines, or any environment handling real funds without conducting thorough security audits, overflow protection, and performance profiling.
> Use at your own risk.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.21631955.svg)](https://doi.org/10.5281/zenodo.21631955)

## Introduction
RED-ARITH (Residue-Enhanced Deterministic Arithmetic) is a numerical model designed for auditable computing...
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

## Citation
Liu Yijing. (2026). RED-ARITH: Tagged-Residue Floating-Point Arithmetic. Zenodo. DOI: 10.5281/zenodo.21690972
