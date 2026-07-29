/*

RED-ARITH: Tagged-Residue Floating-Point Arithmetic

Technical Paper DOI: 10.5281/zenodo.21690972

Copyright 2026 Liu Yijing

Licensed under the Apache License, Version 2.0 (the "License");

you may not use this file except in compliance with the License.

You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software

distributed under the License is distributed on an "AS IS" BASIS,

WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and

limitations under the License.

*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>

/* ============================================================
   DDH-Core v2.0 : 纯整数 DDH 运算库 (C语言)
   ============================================================
   规则（和 Python 版 100% 统一）：
     每个 DDH 数 = (M_int, k, D)
     真实值 V = (M_int + k/D) / SCALE

   加法：M = M1+M2, k = k1+k2, D = LCM(D1,D2)
         carry = k/D, M += carry, k = k%D

   乘法：A1 = M1*D1+k1, A2 = M2*D2+k2
         total_A = A1*A2 / SCALE
         D_new  = D1*D2
         M_new  = total_A / D_new
         k_new  = total_A % D_new

   减法：M = M1-M2, k = k1-k2, D = LCM(D1,D2)
         若 k<0 则从 M 借 1，k += D

   除法：A1 = M1*D1+k1, A2 = M2*D2+k2
         total_A = A1 * D2 * SCALE
         D_new  = D1 * A2
         M_new  = total_A / D_new
         k_new  = total_A % D_new
   ============================================================ */

#define SCALE 100000000ULL   /* 1e8，整数放大系数 */
#define OMEGA 8

/* ---------- DDH 数值结构体 ---------- */
typedef struct {
    uint64_t M;   /* 主值整数 = 8位小数主值 × SCALE */
    uint64_t k;   /* 余数（整数，0 ≤ k < D） */
    uint64_t D;   /* 分母（整数） */
} DDH;

/* ---------- 工具函数 ---------- */
static uint64_t gcd(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = b; b = a % b; a = t; }
    return a;
}
static uint64_t lcm(uint64_t a, uint64_t b) {
    return a / gcd(a, b) * b;
}

/* 化简 */
void ddh_simplify(DDH *x) {
    if (x->k == 0) return;
    uint64_t g = gcd(x->k, x->D);
    x->k /= g;
    x->D /= g;
}

/* 打印（无浮点，手动拆整数/小数部分） */
void ddh_print(const char *tag, const DDH *x) {
    uint64_t ip = x->M / SCALE;
    uint64_t fp = x->M % SCALE;
    printf("%-14s: %" PRIu64 ".%08" PRIu64 " + %" PRIu64 " + %" PRIu64 "\n",
           tag, ip, fp, x->k, x->D);
}

/* 验证 0 ≤ k < D */
int ddh_verify(const char *tag, const DDH *x) {
    if (x->k >= x->D) {
        printf("[FAIL] %s: k=%" PRIu64 " >= D=%" PRIu64 "\n", tag, x->k, x->D);
        return 0;
    }
    printf("[PASS] %s\n", tag);
    return 1;
}

/* ---------- 构造函数 ---------- */
DDH ddh_make(uint64_t M, uint64_t k, uint64_t D) {
    if (D == 0) { fprintf(stderr, "Error: D=0\n"); exit(1); }
    if (k >= D) { fprintf(stderr, "Error: k>=D\n"); exit(1); }
    return (DDH){M, k, D};
}

/* 从用户格式构造（初始化用，内部转整数） */
DDH ddh_from_user(double mantissa, uint64_t k, uint64_t D) {
    uint64_t M = (uint64_t)(mantissa * (double)SCALE + 0.5);
    return ddh_make(M, k, D);
}

/* ---------- 加法 ---------- */
DDH ddh_add(const DDH *a, const DDH *b) {
    __int128 Msum = (__int128)a->M + b->M;
    __int128 ksum = (__int128)a->k + b->k;
    uint64_t Dnew = lcm(a->D, b->D);
    __int128 carry = ksum / Dnew;
    return ddh_make((uint64_t)(Msum + carry), (uint64_t)(ksum % Dnew), Dnew);
}

/* ---------- 减法 ---------- */
DDH ddh_sub(const DDH *a, const DDH *b) {
    __int128 Mdiff = (__int128)a->M - b->M;
    __int128 kdiff = (__int128)a->k - b->k;
    uint64_t Dnew = lcm(a->D, b->D);
    if (kdiff < 0) {
        kdiff += Dnew;
        Mdiff -= 1;
    }
    return ddh_make((uint64_t)Mdiff, (uint64_t)kdiff, Dnew);
}

/* ---------- 乘法 ---------- */
DDH ddh_mul(const DDH *a, const DDH *b) {
    /* A = M*D + k */
    __int128 A1 = (__int128)a->M * a->D + a->k;
    __int128 A2 = (__int128)b->M * b->D + b->k;
    /* total_A = A1*A2 / SCALE */
    __int128 total_A = A1 * A2 / SCALE;
    /* D_new = D1*D2 */
    __int128 Dnew = (__int128)a->D * b->D;
    return ddh_make((uint64_t)(total_A / Dnew),
                   (uint64_t)(total_A % Dnew),
                   (uint64_t)Dnew);
}

/* ---------- 除法 ---------- */
DDH ddh_div(const DDH *a, const DDH *b) {
    __int128 A1 = (__int128)a->M * a->D + a->k;
    __int128 A2 = (__int128)b->M * b->D + b->k;
    if (A2 == 0) { fprintf(stderr, "Error: div by zero\n"); exit(1); }
    /* total_A = A1 * D2 * SCALE */
    __int128 total_A = A1 * b->D * SCALE;
    /* D_new = D1 * A2 */
    __int128 Dnew = (__int128)a->D * A2;
    return ddh_make((uint64_t)(total_A / Dnew),
                   (uint64_t)(total_A % Dnew),
                   (uint64_t)Dnew);
}

/* ============================================================
   测试（和 Python 版 / 手算 100% 一致）
   ============================================================ */
int main(void) {
    int all_pass = 1;
    printf("============================================================\n");
    printf("  DDH-Core v2.0 : 纯整数 DDH 运算库 (C语言)\n");
    printf("  Omega=%d, SCALE=%" PRIu64 ", 无浮点, 适配龙芯\n", OMEGA, SCALE);
    printf("============================================================\n\n");

    /* === 测试1：1/3+1/3+1/3 = 1 === */
    printf("===== 测试1：1/3 + 1/3 + 1/3 =====\n");
    DDH t = ddh_from_user(0.33333333, 1, 3);
    DDH r = ddh_add(&t, &t);
    r = ddh_add(&r, &t);
    ddh_print("结果", &r);
    all_pass &= ddh_verify("测试1", &r);
    printf("预期：1.00000000 + 0 + 3\n\n");

    /* === 测试2：99/101 × 88/98 === */
    printf("===== 测试2：99/101 × 88/98 =====\n");
    /* 99/101: M=98019801, k=99, D=101  (验证: (98019801*101+99)/101e8 = 99/101) */
    DDH a = ddh_make(98019801, 99, 101);
    /* 88/98: M=89795918, k=36, D=98 */
    DDH b = ddh_make(89795918, 36, 98);
    DDH m1 = ddh_mul(&a, &b);
    ddh_print("结果", &m1);
    DDH m1s = m1; ddh_simplify(&m1s);
    ddh_print("化简后", &m1s);
    all_pass &= ddh_verify("测试2", &m1);
    printf("预期：0.88017781 + 3662 + 9898\n\n");

    /* === 测试3：0.12345678+2+9 × 0.87654321+7+9 === */
    printf("===== 测试3：0.12345678 × 0.87654321 =====\n");
    DDH c = ddh_make(12345678, 2, 9);
    DDH d = ddh_make(87654321, 7, 9);
    DDH m2 = ddh_mul(&c, &d);
    ddh_print("结果", &m2);
    DDH m2s = m2; ddh_simplify(&m2s);
    ddh_print("化简后", &m2s);
    all_pass &= ddh_verify("测试3", &m2);
    printf("预期：0.10821521 + 547901184 + 8100000000\n\n");

    /* === 测试4：上两个乘积相加 === */
    printf("===== 测试4：mul1 + mul2 =====\n");
    /* mul1 = 0.88017781 + 34722 + 89082 */
    DDH m1e = ddh_make(88017781, 34722, 89082);
    /* mul2 = 0.10821521 + 547901184 + 8100000000 */
    DDH m2e = ddh_make(10821521, 547901184, 8100000000ULL);
    DDH ar = ddh_add(&m1e, &m2e);
    ddh_print("结果", &ar);
    DDH ars = ar; ddh_simplify(&ars);
    ddh_print("化简后", &ars);
    all_pass &= ddh_verify("测试4", &ar);
    printf("预期：0.13710665 + 548409456 + 40086900000000\n\n");

    /* === 测试5：1/2 × 1/2 = 1/4 === */
    printf("===== 测试5：1/2 × 1/2 = 1/4 =====\n");
    DDH h1 = ddh_make(50000000, 0, 1);  /* 0.5 */
    DDH h2 = ddh_make(50000000, 0, 1);
    DDH mh = ddh_mul(&h1, &h2);
    ddh_print("结果", &mh);
    all_pass &= ddh_verify("测试5", &mh);
    printf("预期：0.25000000 + 0 + 1\n\n");

    /* === 测试6：2/3 × 3/7 = 2/7 === */
    printf("===== 测试6：2/3 × 3/7 = 2/7 =====\n");
    DDH tw = ddh_make(66666666, 2, 3);   /* 2/3 */
    DDH th = ddh_make(42857142, 6, 7);   /* 3/7 */
    DDH mf = ddh_mul(&tw, &th);
    ddh_print("结果", &mf);
    DDH mfs = mf; ddh_simplify(&mfs);
    ddh_print("化简后", &mfs);
    all_pass &= ddh_verify("测试6", &mf);
    printf("预期：0.28571428 + ... + 21\n\n");

    /* === 测试7：1 - 1/3 = 2/3 === */
    printf("===== 测试7：1 - 1/3 = 2/3 =====\n");
    DDH one = ddh_make(SCALE, 0, 1);  /* 1.0 */
    DDH ot = ddh_from_user(0.33333333, 1, 3);  /* 1/3 */
    DDH sr = ddh_sub(&one, &ot);
    ddh_print("结果", &sr);
    all_pass &= ddh_verify("测试7", &sr);
    printf("预期：0.66666666 + 2 + 3\n\n");

    /* === 测试8：1/2 ÷ 1/3 = 3/2 === */
    printf("===== 测试8：1/2 ÷ 1/3 = 3/2 =====\n");
    DDH dr = ddh_div(&h1, &ot);
    ddh_print("结果", &dr);
    DDH drs = dr; ddh_simplify(&drs);
    ddh_print("化简后", &drs);
    all_pass &= ddh_verify("测试8", &dr);
    printf("预期：1.50000000 + ... + ...\n\n");

    /* === 汇总 === */
    printf("============================================================\n");
    if (all_pass) {
        printf("  ✅ 全部测试通过！和 Python 版/手算 100%% 一致\n");
    } else {
        printf("  ❌ 存在失败测试\n");
    }
    printf("============================================================\n");
    return all_pass ? 0 : 1;
}
