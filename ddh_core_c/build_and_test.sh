#!/bin/bash
# DDH-Core 自动编译测试脚本
# 支持 x86 / ARM / 龙芯 LoongArch

set -e

echo "=========================================="
echo "  DDH-Core 自动编译测试"
echo "=========================================="
echo ""

# 检测编译器
if command -v loongarch64-unknown-linux-gnu-gcc &> /dev/null; then
    CC="loongarch64-unknown-linux-gnu-gcc"
    echo "[INFO] 检测到龙芯 LoongArch GCC"
elif command -v gcc &> /dev/null; then
    CC="gcc"
    echo "[INFO] 检测到系统 GCC"
elif command -v clang &> /dev/null; then
    CC="clang"
    echo "[INFO] 检测到 Clang"
else
    echo "[ERROR] 未找到可用的 C 编译器 (gcc/clang/loongarch64-gcc)"
    exit 1
fi

echo "[INFO] 使用编译器: $CC"
echo ""

# 编译
echo "==== 编译中... ===="
$CC -O2 -std=c11 -Wall -Wextra -Wpedantic -o ddh_core ddh_core.c
echo "[OK] 编译成功 → ddh_core"
echo ""

# 运行测试
echo "==== 运行测试... ===="
./ddh_core
echo ""

# 检查返回值
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "[OK] 全部测试通过！"
    echo "=========================================="
else
    echo "=========================================="
    echo "[FAIL] 测试失败，请检查代码"
    echo "=========================================="
    exit 1
fi
