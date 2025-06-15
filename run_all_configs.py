#!/usr/bin/env python6
"""
自動運行所有MESI配置並收集數據
"""

import os
import subprocess
import json
import shutil
from datetime import datetime

def run_simulation(config_name, script_path, output_dir):
    """運行單個模擬配置"""
    print(f"\n🚀 運行配置: {config_name}")
    print("=" * 50)
    
    try:
        # 運行gem5模擬
        cmd = f"./build/RISCV/gem5.opt {script_path}"
        print(f"執行命令: {cmd}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ {config_name} 運行失敗:")
            print(result.stderr)
            return False
        
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)
        
        # 複製統計文件
        if os.path.exists("m5out/stats.txt"):
            shutil.copy("m5out/stats.txt", f"{output_dir}/stats.txt")
            print(f"✅ {config_name} 運行成功，統計文件已保存")
            return True
        else:
            print(f"❌ {config_name} 統計文件未找到")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {config_name} 運行超時")
        return False
    except Exception as e:
        print(f"❌ {config_name} 運行出錯: {e}")
        return False

def main():
    """主函數：運行所有配置"""
    print("🎯 開始運行三種MESI配置比較")
    print("=" * 60)
    
    # 配置信息
    configurations = [
        {
            'name': 'Small Cache',
            'script': 'configs/scripts/mesi_small_cache.py',
            'output_dir': 'results/small_cache',
            'description': 'L1=16KB, L2=256KB'
        },
        {
            'name': 'Medium Cache', 
            'script': 'configs/scripts/mesi_system.py',
            'output_dir': 'results/medium_cache',
            'description': 'L1=32KB, L2=512KB'
        },
        {
            'name': 'Large Cache',
            'script': 'configs/scripts/mesi_large_cache.py', 
            'output_dir': 'results/large_cache',
            'description': 'L1=64KB, L2=1MB'
        }
    ]
    
    # 創建結果目錄
    os.makedirs('results', exist_ok=True)
    
    # 記錄開始時間
    start_time = datetime.now()
    results = {}
    
    # 運行所有配置
    for config in configurations:
        success = run_simulation(
            config['name'], 
            config['script'], 
            config['output_dir']
        )
        
        results[config['name']] = {
            'success': success,
            'description': config['description'],
            'output_dir': config['output_dir']
        }
    
    # 記錄結束時間
    end_time = datetime.now()
    duration = end_time - start_time
    
    # 生成運行報告
    print(f"\n📊 運行完成！總耗時: {duration}")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✅ 成功" if result['success'] else "❌ 失敗"
        print(f"{name} ({result['description']}): {status}")
    
    # 保存運行信息
    run_info = {
        'timestamp': start_time.isoformat(),
        'duration': str(duration),
        'configurations': results
    }
    
    with open('results/run_info.json', 'w') as f:
        json.dump(run_info, f, indent=2)
    
    print(f"\n📁 所有結果保存在 'results/' 目錄中")
    print("接下來運行數據分析和圖表生成腳本:")
    print("python3 compare_mesi_configs.py")

if __name__ == "__main__":
    main() 