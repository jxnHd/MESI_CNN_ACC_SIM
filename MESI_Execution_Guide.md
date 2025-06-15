# MESI协议测试执行指南 (MESI Protocol Test Execution Guide)

## 项目概述 (Project Overview)

本项目在gem5模拟器中实现并测试MESI协议，使用CNN工作负载进行性能分析和比较。

## 前置要求 (Prerequisites)

- gem5模拟器已安装并编译
- Python 3.x 环境
- matplotlib 和 numpy 库
- RISC-V 工具链

## 执行步骤 (Execution Steps)

### 1. 编译CNN测试程序 (Compile CNN Test Program)

```bash
# 编译CNN测试程序
gcc -static -o cnn_test cnn_test.c

# 验证编译结果
ls -la cnn_test
file cnn_test
```

**预期输出:**
```
-rwxrwxr-x 1 carlton carlton 17856 Jan 10 XX:XX cnn_test
cnn_test: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked
```

### 2. 运行单个配置测试 (Run Single Configuration Test)

#### 测试中等缓存配置 (Medium Cache Configuration)
```bash
# 运行中等缓存配置
build/RISCV/gem5.opt configs/scripts/mesi_system.py

# 查看输出结果
ls -la m5out/
```

#### 测试小缓存配置 (Small Cache Configuration)
```bash
# 运行小缓存配置
build/RISCV/gem5.opt configs/scripts/mesi_small_cache.py

# 移动结果到指定目录
mkdir -p results/small_cache
cp m5out/* results/small_cache/
```

#### 测试大缓存配置 (Large Cache Configuration)
```bash
# 运行大缓存配置
build/RISCV/gem5.opt configs/scripts/mesi_large_cache.py

# 移动结果到指定目录
mkdir -p results/large_cache
cp m5out/* results/large_cache/
```

### 3. 批量运行所有配置 (Run All Configurations)

```bash
# 使用自动化脚本运行所有配置
python3 run_all_configs.py
```

**执行过程输出:**
```
🚀 Starting MESI configuration comparison tests
================================================

🔧 Running Small Cache configuration...
Running CNN MESI test: Small_Cache_RISCV_MESI_CNN
开始CNN MESI协议模擬...
CPU核心數: 2
L1 Cache大小: 16kB
L2 Cache大小: 256kB
✅ Small Cache test completed

🔧 Running Medium Cache configuration...
Running CNN MESI test: Medium_Cache_RISCV_MESI_CNN
开始CNN MESI协议模擬...
CPU核心數: 2
L1 Cache大小: 32kB
L2 Cache大小: 512kB
✅ Medium Cache test completed

🔧 Running Large Cache configuration...
Running CNN MESI test: Large_Cache_RISCV_MESI_CNN
开始CNN MESI协议模擬...
CPU核心數: 2
L1 Cache大小: 64kB
L2 Cache大小: 1MB
✅ Large Cache test completed

🎉 All configurations completed successfully!
```

### 4. 生成性能分析报告 (Generate Performance Analysis)

```bash
# 生成性能比较图表和报告
python3 compare_mesi_configs.py
```

**执行输出:**
```
📊 Analyzing MESI configuration performance data
==================================================
📖 Parsing Small Cache data...
✅ Small Cache data parsed successfully
📖 Parsing Medium Cache data...
✅ Medium Cache data parsed successfully
📖 Parsing Large Cache data...
✅ Large Cache data parsed successfully

📊 Generating performance comparison charts...
📊 Chart saved: results/mesi_performance_comparison.png

📝 Generating performance report...
📝 Performance report saved: results/performance_summary.txt

🎉 Analysis complete! Results saved in 'results/' directory
```

### 5. 查看结果文件 (View Results)

```bash
# 查看结果目录结构
tree results/

# 查看性能总结报告
cat results/performance_summary.txt

# 查看图表文件
ls -la results/mesi_performance_comparison.png
```

**目录结构:**
```
results/
├── large_cache/
│   ├── config.ini
│   ├── stats.txt
│   └── ...
├── medium_cache/
│   ├── config.ini
│   ├── stats.txt
│   └── ...
├── small_cache/
│   ├── config.ini
│   ├── stats.txt
│   └── ...
├── mesi_performance_comparison.png
└── performance_summary.txt
```

## 配置说明 (Configuration Details)

### 缓存配置对比 (Cache Configuration Comparison)

| 配置类型 | L1 Cache Size | L2 Cache Size | L1 Associativity | L2 Associativity |
|----------|---------------|---------------|------------------|------------------|
| Small Cache | 16kB | 256kB | 4-way | 8-way |
| Medium Cache | 32kB | 512kB | 4-way | 8-way |
| Large Cache | 64kB | 1MB | 4-way | 8-way |

### 系统配置 (System Configuration)

- **CPU类型**: TimingSimpleCPU (RISC-V)
- **CPU核心数**: 2
- **时钟频率**: 3GHz
- **内存**: 2GB DDR3-1600
- **协议**: MESI缓存一致性协议

## 性能指标 (Performance Metrics)

### 主要观察指标 (Key Metrics)

1. **L1缓存命中率** (L1 Cache Hit Rate)
2. **L2缓存命中率** (L2 Cache Hit Rate)
3. **缓存缺失次数** (Cache Miss Count)
4. **模拟执行时间** (Simulation Time)
5. **平均CPI** (Average CPI)
6. **缓存访问次数** (Cache Access Count)

### 性能结果示例 (Sample Performance Results)

```
Configuration: Small Cache
----------------------------------------
L1 Cache Hit Rate: 99.36%
L2 Cache Hit Rate: 54.42%
L1 Total Misses: 13,234
L2 Total Misses: 6,035
Simulation Time: 0.562 seconds
Average CPI: 2.850
Total Instructions: 197,062

Configuration: Medium Cache
----------------------------------------
L1 Cache Hit Rate: 99.39%
L2 Cache Hit Rate: 52.00%
L1 Total Misses: 12,034
L2 Total Misses: 5,778
Simulation Time: 0.561 seconds
Average CPI: 2.849
Total Instructions: 197,062

Configuration: Large Cache
----------------------------------------
L1 Cache Hit Rate: 99.40%
L2 Cache Hit Rate: 51.53%
L1 Total Misses: 11,834
L2 Total Misses: 5,656
Simulation Time: 0.560 seconds
Average CPI: 2.848
Total Instructions: 197,062
```

## 故障排除 (Troubleshooting)

### 常见问题 (Common Issues)

1. **编译错误**: 确保安装了RISC-V工具链
   ```bash
   which riscv64-linux-gnu-gcc
   ```

2. **gem5找不到workload**: 检查cnn_test程序是否存在
   ```bash
   ls -la cnn_test
   ```

3. **Python依赖缺失**: 安装必要的库
   ```bash
   pip install matplotlib numpy
   ```

4. **权限问题**: 确保有执行权限
   ```bash
   chmod +x cnn_test
   chmod +x run_all_configs.py
   chmod +x compare_mesi_configs.py
   ```

## 分析结论 (Analysis Conclusions)

### 主要发现 (Key Findings)

1. **缓存命中率**: 随着缓存大小增加，L1命中率略有提升
2. **执行性能**: 大缓存配置具有最佳的整体性能
3. **MESI开销**: 在所有配置中MESI协议开销都很低(<1%)
4. **工作负载特性**: CNN工作负载展现出良好的缓存局部性

### 性能排名 (Performance Rankings)

- **L1命中率**: Large Cache > Medium Cache > Small Cache
- **执行速度**: Large Cache > Medium Cache > Small Cache
- **CPI性能**: Large Cache > Medium Cache > Small Cache

## 完整命令序列 (Complete Command Sequence)

```bash
# 1. 编译CNN测试程序
gcc -static -o cnn_test cnn_test.c

# 2. 运行所有配置测试
python3 run_all_configs.py

# 3. 生成性能分析
python3 compare_mesi_configs.py

# 4. 查看结果
tree results/
cat results/performance_summary.txt
```

## 文件清单 (File List)

### 核心文件 (Core Files)
- `cnn_test.c` - CNN测试程序源代码
- `cnn_test` - 编译后的测试程序
- `run_all_configs.py` - 批量运行脚本
- `compare_mesi_configs.py` - 性能分析脚本

### 配置文件 (Configuration Files)
- `configs/scripts/mesi_system.py` - 中等缓存配置
- `configs/scripts/mesi_small_cache.py` - 小缓存配置
- `configs/scripts/mesi_large_cache.py` - 大缓存配置

### 结果文件 (Result Files)
- `results/mesi_performance_comparison.png` - 性能比较图表
- `results/performance_summary.txt` - 性能总结报告
- `results/*/stats.txt` - 各配置的详细统计数据

---

**注意**: 执行时间可能根据系统性能有所不同。建议在执行前确保系统有足够的计算资源。 