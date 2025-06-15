# MESI協議觀察指南

本指南將幫助您觀察gem5 CNN模擬中的MESI協議過程。

## 1. 運行基本模擬

```bash
# 運行基本CNN MESI模擬
./build/RISCV/gem5.opt configs/scripts/mesi_system.py
```

## 2. 運行帶調試輸出的模擬

```bash
# 運行帶緩存調試標誌的模擬
./build/RISCV/gem5.opt \
  --debug-flags=Cache,CacheComp,CachePort,CacheTags \
  --debug-file=cache_debug.txt \
  --debug-start=1000000 \
  configs/scripts/mesi_system.py
```

## 3. 分析統計信息

### 查看緩存統計
```bash
# 查看L1和L2緩存統計
grep -E "(l1_dcache|l2cache)" m5out/stats.txt

# 查看緩存命中率
grep -E "(demandHits|demandMisses|demandMissRate)" m5out/stats.txt
```

### 運行分析腳本
```bash
python3 analyze_mesi.py
```

## 4. MESI協議狀態說明

- **Modified (M)**: 緩存行已被修改，且只存在於當前緩存中
- **Exclusive (E)**: 緩存行未被修改，但只存在於當前緩存中
- **Shared (S)**: 緩存行存在於多個緩存中，且未被修改
- **Invalid (I)**: 緩存行無效

## 5. 觀察要點

### CNN工作負載的MESI特性
- **卷積運算**: 大量讀取操作，容易產生Shared狀態
- **池化操作**: 讀寫混合，可能產生Modified狀態
- **跨核心通信**: 觸發Invalid到Shared的轉換

### 關鍵指標
- L1緩存命中率
- L2緩存命中率 
- 緩存間一致性開銷
- 狀態轉換頻率

## 6. 調試輸出分析

查看生成的調試文件：
```bash
# 查看緩存事件
grep -E "(Cache|hit|miss)" cache_debug.txt | head -20

# 查看一致性事件
grep -E "(coherence|invalidate|shared)" cache_debug.txt | head -10
```

## 7. 統計信息解讀

### L1 Data Cache統計
- `demandHits`: 需求訪問命中次數
- `demandMisses`: 需求訪問缺失次數
- `demandMissRate`: 需求訪問缺失率

### L2 Cache統計
- 共享L2緩存的統計信息
- 反映跨核心數據共享情況

## 8. MESI協議觀察工具

使用內建的CNN加速器MESI監控功能：
- 在模擬開始時自動顯示MESI狀態轉換
- 提供樣本地址的狀態變化
- 模擬典型的MESI協議行為

## 9. 進階調試

### 啟用更詳細的調試
```bash
./build/RISCV/gem5.opt \
  --debug-flags=Cache,CacheComp,CachePort,CacheTags,CacheVerbose \
  --debug-file=detailed_cache.txt \
  --debug-start=500000 \
  --debug-end=1500000 \
  configs/scripts/mesi_system.py
```

### 分析特定時間段
- 使用`--debug-start`和`--debug-end`限制輸出範圍
- 減少調試文件大小，專注於關鍵時期

## 10. 預期觀察結果

### 雙核CNN模擬中的MESI行為
1. **初始化階段**: 大量Invalid到Exclusive轉換
2. **卷積計算**: Exclusive到Shared轉換（數據共享）
3. **寫入操作**: Shared/Exclusive到Modified轉換
4. **一致性維護**: Modified到Invalid轉換（其他核心訪問）

### 典型統計數據範圍
- L1命中率: 90-95%
- L2命中率: 95-99%
- 一致性開銷: 5-15%

這些工具和方法將幫助您深入理解gem5 CNN模擬中的MESI協議行為。 