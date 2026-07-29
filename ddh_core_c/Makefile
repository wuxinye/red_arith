# Makefile for DDH-Core (C语言纯整数DDH运算库)
# 适配龙芯 LoongArch / x86 GCC / ARM GCC

CC      ?= gcc
CFLAGS  ?= -O2 -std=c11 -Wall -Wextra -Wpedantic
TARGET  := ddh_core
SRC     := ddh_core.c

# 默认目标
all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $<

# 运行测试
run: $(TARGET)
	./$(TARGET)

# 清理
clean:
	rm -f $(TARGET)

# 龙芯专用编译（指定LoongArch GCC）
loongarch:
	loongarch64-unknown-linux-gnu-gcc $(CFLAGS) -o $(TARGET) $(SRC)

.PHONY: all run clean loongarch
