# File: configs/scripts/mesi_large_cache.py
import m5
from m5.objects import *
import sys
import os

# 添加路徑
gem5_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(gem5_root, 'config'))

from cache_config import L1Cache, L1ICache, L1DCache, L2Cache

def build_system(config):
    system = System()
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '3GHz'
    system.clk_domain.voltage_domain = VoltageDomain()
    
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]

    # 關鍵修正：添加RISC-V SEWorkload
    system.workload = RiscvEmuLinux()

    # 記憶體配置
    system.membus = SystemXBar()
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # CPU配置
    system.cpu = [TimingSimpleCPU(cpu_id=i) for i in range(config['num_cores'])]
    
    # 关键修正：为RISC-V CPU添加中断控制器
    for i, cpu in enumerate(system.cpu):
        cpu.interrupts = [RiscvInterrupts()]
    
    # 關鍵修正：使用CNN測試程序
    cnn_test_path = os.path.join(gem5_root, 'cnn_test')
    if not os.path.exists(cnn_test_path):
        print(f"Warning: CNN test program not found at {cnn_test_path}")
        print("Please compile cnn_test.c first!")
        cnn_test_path = '/bin/true'  # 備選方案
    
    print(f"Using CNN test program: {cnn_test_path}")
    
    # 為每個CPU分配CNN工作負載
    for i, cpu in enumerate(system.cpu):
        process = Process()
        process.cmd = [cnn_test_path]
        process.pid = 100 + i  # 为每个进程分配不同的PID
        cpu.workload = process
        cpu.createThreads()
    
    # Cache配置 - 大缓存
    system.l1_icache = [L1ICache() for _ in range(config['num_cores'])]
    system.l1_dcache = [L1DCache() for _ in range(config['num_cores'])]
    system.l2cache = L2Cache()
    system.l2bus = L2XBar()
    
    # 連接組件
    for i in range(config['num_cores']):
        system.l1_icache[i].size = config['l1_size']
        system.l1_dcache[i].size = config['l1_size']
        
        system.cpu[i].icache_port = system.l1_icache[i].cpu_side
        system.cpu[i].dcache_port = system.l1_dcache[i].cpu_side
        
        system.l1_icache[i].mem_side = system.l2bus.cpu_side_ports
        system.l1_dcache[i].mem_side = system.l2bus.cpu_side_ports

    system.l2cache.size = config['l2_size']
    system.l2cache.assoc = config['l2_assoc']
    system.l2cache.cpu_side = system.l2bus.mem_side_ports
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # CNN加速器配置
    system.cnn_accel = CNNAccelerator()
    system.cnn_accel.cache_port = system.membus.cpu_side_ports
    system.cnn_accel.dma_port = system.membus.cpu_side_ports

    system.system_port = system.membus.cpu_side_ports
    return system

def main():
    config = {
        'name': 'RISCV_MESI_CNN_LARGE',
        'num_cores': 2, 
        'l1_size': '64kB',    # 大L1缓存
        'l1_assoc': 8, 
        'l2_size': '1MB',     # 大L2缓存
        'l2_assoc': 16
    }
    
    print(f"Running CNN MESI LARGE CACHE test: {config['name']}")
    
    system = build_system(config)
    root = Root(full_system=False, system=system)
    
    m5.instantiate()
    
    print(f"開始CNN MESI協議模擬（大缓存配置）...")
    print(f"CPU核心數: {config['num_cores']}")
    print(f"L1 Cache大小: {config['l1_size']}")
    print(f"L2 Cache大小: {config['l2_size']}")
    print("MESI協議狀態監控將自動啟動...")
    
    exit_event = m5.simulate()
    print(f"CNN模擬結束，原因: {exit_event.getCause()}")

if __name__ == "__m5_main__":
    main() 