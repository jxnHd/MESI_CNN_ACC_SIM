// File: src/cnn_accelerator/cnn_accelerator.cc
#include "cnn_accelerator/cnn_accelerator.hh"
#include <iostream>

namespace gem5 {

// 關鍵修正：使用成員初始化列表
CNNAccelerator::CNNAccelerator(const CNNAcceleratorParams &p)
  : ClockedObject(p),                    // 使用初始化列表調用基類構造函數
    cache_port("cache_port", this),      // 初始化端口
    dma_port("dma_port", this)          // 初始化端口
{
    // 構造函數體為空，所有初始化在初始化列表中完成
    std::cout << "[CNNAccelerator] Initialized at tick " << curTick() << std::endl;
    std::cout << "[CNNAccelerator] Ready to monitor MESI protocol" << std::endl;
    
    // 自动调用MESI协议状态模拟
    simulateMESIStates();
}

// 关键修正：实现getPort方法
Port &CNNAccelerator::getPort(const std::string &if_name, PortID idx) {
    if (if_name == "cache_port") {
        return cache_port;
    } else if (if_name == "dma_port") {
        return dma_port;
    } else {
        return ClockedObject::getPort(if_name, idx);
    }
}

void CNNAccelerator::printMESIState(Addr addr, int state) {
    std::cout << "[CNNAccelerator MESI] Tick: " << curTick() 
              << " | Addr: 0x" << std::hex << addr << std::dec
              << " | State: " << stateToString(state) 
              << " | Transition detected" << std::endl;
}

const char* CNNAccelerator::stateToString(int state) {
    switch(state) {
        case 0: return "Invalid (I)";
        case 1: return "Shared (S)";
        case 2: return "Exclusive (E)"; 
        case 3: return "Modified (M)";
        default: return "Unknown";
    }
}

// 新增：模擬MESI協議狀態監控
void CNNAccelerator::simulateMESIStates() {
    std::cout << "\n=== CNN Accelerator MESI Protocol Simulation ===" << std::endl;
    
    // 模擬不同的MESI狀態轉換
    Addr sample_addrs[] = {0x1000, 0x2000, 0x3000, 0x4000};
    int sample_states[] = {0, 1, 2, 3}; // I, S, E, M
    
    for (int i = 0; i < 4; i++) {
        printMESIState(sample_addrs[i], sample_states[i]);
        
        // 模擬狀態轉換
        if (i < 3) {
            std::cout << "[CNNAccelerator MESI] Simulating state transition..." << std::endl;
            printMESIState(sample_addrs[i], (sample_states[i] + 1) % 4);
        }
    }
    
    std::cout << "=== MESI Protocol Simulation Complete ===" << std::endl;
}

} // namespace gem5

