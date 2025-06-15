#!/bin/bash
# File: compile_cnn_test.sh

echo "Compiling CNN test for RISC-V..."

# 檢查是否有RISC-V工具鏈
if command -v riscv64-unknown-linux-gnu-gcc &> /dev/null; then
    COMPILER="riscv64-unknown-linux-gnu-gcc"
elif command -v riscv64-linux-gnu-gcc &> /dev/null; then
    COMPILER="riscv64-linux-gnu-gcc"
else
    echo "Error: RISC-V compiler not found!"
    echo "Please install riscv64-unknown-linux-gnu-gcc or riscv64-linux-gnu-gcc"
    exit 1
fi

echo "Using compiler: $COMPILER"

# 編譯為靜態連結的RISC-V程序
$COMPILER -static -O2 -march=rv64gc -mabi=lp64d \
    -o cnn_test cnn_test.c -lm

if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    echo "Generated: cnn_test"
    file cnn_test
else
    echo "Compilation failed!"
    exit 1
fi

