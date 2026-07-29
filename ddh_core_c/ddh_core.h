#ifndef DDH_CORE_H
#define DDH_CORE_H

/*
 * DDH-Core 头文件 (C语言)
 * 纯整数 DDH 运算库 - 对外API声明
 * Ω=8，最小单位1e-8，全程无浮点
 */

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* DDH数值结构体 */
typedef struct {
    uint64_t M;   /* 主值整数 = 8位小数主值 × SCALE */
    uint64_t k;   /* 余数，整数，满足 0 ≤ k < D */
    uint64_t D;   /* 分母，整数 */
} DDH;

/* 核心常量 */
#define DDH_SCALE  100000000ULL   /* 1e8 */
#define DDH_OMEGA 8

/* ===== 构造函数 ===== */
DDH ddh_make(uint64_t M, uint64_t k, uint64_t D);
DDH ddh_from_user(double mantissa, uint64_t k, uint64_t D);

/* ===== 核心运算 ===== */
DDH ddh_add(const DDH *a, const DDH *b);   /* 加法 */
DDH ddh_sub(const DDH *a, const DDH *b);   /* 减法 */
DDH ddh_mul(const DDH *a, const DDH *b);   /* 乘法 */
DDH ddh_div(const DDH *a, const DDH *b);   /* 除法 */

/* ===== 工具函数 ===== */
void ddh_simplify(DDH *x);              /* 化简余数/分母 */
void ddh_print(const char *tag, const DDH *x);  /* 打印 */
int  ddh_verify(const char *tag, const DDH *x); /* 验证 */

#ifdef __cplusplus
}
#endif

#endif /* DDH_CORE_H */
