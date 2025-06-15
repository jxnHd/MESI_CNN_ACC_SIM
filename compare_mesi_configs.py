#!/usr/bin/env python3
"""
MESI配置性能比较和图表生成脚本
"""

import re
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 设置matplotlib字体（移除中文字体设置）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def parse_stats_file(stats_file):
    """解析gem5统计文件"""
    if not os.path.exists(stats_file):
        print(f"统计文件不存在: {stats_file}")
        return None
    
    stats = {}
    
    try:
        with open(stats_file, 'r') as f:
            content = f.read()
        
        # 解析L1缓存统计
        l1_patterns = {
            'l1_hits_cpu0': r'system\.l1_dcache0\.demandHits::total\s+(\d+)',
            'l1_misses_cpu0': r'system\.l1_dcache0\.demandMisses::total\s+(\d+)',
            'l1_accesses_cpu0': r'system\.l1_dcache0\.demandAccesses::total\s+(\d+)',
            'l1_miss_rate_cpu0': r'system\.l1_dcache0\.demandMissRate::total\s+([0-9.]+)',
            'l1_hits_cpu1': r'system\.l1_dcache1\.demandHits::total\s+(\d+)',
            'l1_misses_cpu1': r'system\.l1_dcache1\.demandMisses::total\s+(\d+)',
            'l1_accesses_cpu1': r'system\.l1_dcache1\.demandAccesses::total\s+(\d+)',
            'l1_miss_rate_cpu1': r'system\.l1_dcache1\.demandMissRate::total\s+([0-9.]+)'
        }
        
        # 解析L2缓存统计
        l2_patterns = {
            'l2_hits': r'system\.l2cache\.demandHits::total\s+(\d+)',
            'l2_misses': r'system\.l2cache\.demandMisses::total\s+(\d+)',
            'l2_accesses': r'system\.l2cache\.demandAccesses::total\s+(\d+)',
            'l2_miss_rate': r'system\.l2cache\.demandMissRate::total\s+([0-9.]+)'
        }
        
        # 解析性能统计
        perf_patterns = {
            'sim_seconds': r'simSeconds\s+([0-9.]+)',
            'sim_insts': r'simInsts\s+(\d+)',
            'host_inst_rate': r'hostInstRate\s+(\d+)',
            'cpi_cpu0': r'system\.cpu0\.cpi\s+([0-9.]+)',
            'cpi_cpu1': r'system\.cpu1\.cpi\s+([0-9.]+)'
        }
        
        # 提取所有模式
        all_patterns = {**l1_patterns, **l2_patterns, **perf_patterns}
        
        for key, pattern in all_patterns.items():
            match = re.search(pattern, content)
            if match:
                try:
                    value = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
                    stats[key] = value
                except ValueError:
                    stats[key] = 0
            else:
                stats[key] = 0
        
        # 计算总计值
        stats['l1_total_hits'] = stats.get('l1_hits_cpu0', 0) + stats.get('l1_hits_cpu1', 0)
        stats['l1_total_misses'] = stats.get('l1_misses_cpu0', 0) + stats.get('l1_misses_cpu1', 0)
        stats['l1_total_accesses'] = stats.get('l1_accesses_cpu0', 0) + stats.get('l1_accesses_cpu1', 0)
        
        if stats['l1_total_accesses'] > 0:
            stats['l1_total_hit_rate'] = stats['l1_total_hits'] / stats['l1_total_accesses'] * 100
            stats['l1_total_miss_rate'] = stats['l1_total_misses'] / stats['l1_total_accesses'] * 100
        else:
            stats['l1_total_hit_rate'] = 0
            stats['l1_total_miss_rate'] = 0
        
        if stats.get('l2_accesses', 0) > 0:
            stats['l2_hit_rate'] = stats.get('l2_hits', 0) / stats['l2_accesses'] * 100
        else:
            stats['l2_hit_rate'] = 0
        
        # 计算平均CPI
        stats['avg_cpi'] = (stats.get('cpi_cpu0', 0) + stats.get('cpi_cpu1', 0)) / 2
        
        return stats
        
    except Exception as e:
        print(f"解析统计文件出错: {e}")
        return None

def generate_comparison_charts(all_stats):
    """生成比较图表"""
    configurations = list(all_stats.keys())
    
    # 创建图表
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('MESI Protocol Configuration Performance Comparison', fontsize=16, fontweight='bold')
    
    # 1. L1缓存命中率比较
    ax1 = axes[0, 0]
    l1_hit_rates = [all_stats[config]['l1_total_hit_rate'] for config in configurations]
    bars1 = ax1.bar(configurations, l1_hit_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax1.set_title('L1 Cache Hit Rate (%)')
    ax1.set_ylabel('Hit Rate (%)')
    ax1.set_ylim(90, 100)
    
    # 添加数值标签
    for bar, rate in zip(bars1, l1_hit_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{rate:.2f}%', ha='center', va='bottom')
    
    # 2. L2缓存命中率比较
    ax2 = axes[0, 1]
    l2_hit_rates = [all_stats[config]['l2_hit_rate'] for config in configurations]
    bars2 = ax2.bar(configurations, l2_hit_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax2.set_title('L2 Cache Hit Rate (%)')
    ax2.set_ylabel('Hit Rate (%)')
    
    for bar, rate in zip(bars2, l2_hit_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom')
    
    # 3. 缓存缺失次数比较
    ax3 = axes[0, 2]
    l1_misses = [all_stats[config]['l1_total_misses'] for config in configurations]
    l2_misses = [all_stats[config]['l2_misses'] for config in configurations]
    
    x = np.arange(len(configurations))
    width = 0.35
    
    bars3a = ax3.bar(x - width/2, l1_misses, width, label='L1 Misses', color='#FF9999')
    bars3b = ax3.bar(x + width/2, l2_misses, width, label='L2 Misses', color='#66B2FF')
    
    ax3.set_title('Cache Miss Count Comparison')
    ax3.set_ylabel('Miss Count')
    ax3.set_xticks(x)
    ax3.set_xticklabels(configurations)
    ax3.legend()
    
    # 4. 模拟时间比较
    ax4 = axes[1, 0]
    sim_times = [all_stats[config]['sim_seconds'] for config in configurations]
    bars4 = ax4.bar(configurations, sim_times, color=['#FFB84D', '#A8E6CF', '#D1A3FF'])
    ax4.set_title('Simulation Time (seconds)')
    ax4.set_ylabel('Time (seconds)')
    
    for bar, time in zip(bars4, sim_times):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{time:.3f}s', ha='center', va='bottom')
    
    # 5. CPI比较
    ax5 = axes[1, 1]
    cpis = [all_stats[config]['avg_cpi'] for config in configurations]
    bars5 = ax5.bar(configurations, cpis, color=['#FF8C94', '#FFD3A5', '#FFA3FD'])
    ax5.set_title('Average CPI (Cycles Per Instruction)')
    ax5.set_ylabel('CPI')
    
    for bar, cpi in zip(bars5, cpis):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{cpi:.2f}', ha='center', va='bottom')
    
    # 6. 缓存访问次数对比
    ax6 = axes[1, 2]
    
    l1_accesses = [all_stats[config]['l1_total_accesses'] for config in configurations]
    l2_accesses = [all_stats[config]['l2_accesses'] for config in configurations]
    
    x = np.arange(len(configurations))
    width = 0.35
    
    bars6a = ax6.bar(x - width/2, l1_accesses, width, label='L1 Accesses', color='#FFB6C1')
    bars6b = ax6.bar(x + width/2, l2_accesses, width, label='L2 Accesses', color='#87CEEB')
    
    ax6.set_title('Cache Access Count Comparison')
    ax6.set_ylabel('Access Count')
    ax6.set_xticks(x)
    ax6.set_xticklabels(configurations)
    ax6.legend()
    
    # 添加数值标签
    for bar in bars6a:
        height = bar.get_height()
        if height > 0:
            ax6.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height/1000)}K', ha='center', va='bottom', fontsize=8)
    
    for bar in bars6b:
        height = bar.get_height()
        if height > 0:
            ax6.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height/1000)}K', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    # 保存图表
    chart_file = 'results/mesi_performance_comparison.png'
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    print(f"📊 Chart saved: {chart_file}")
    
    # 显示图表
    plt.show()

def generate_summary_report(all_stats):
    """生成总结报告"""
    report_file = 'results/performance_summary.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("MESI Protocol Configuration Performance Comparison Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for config_name, stats in all_stats.items():
            f.write(f"Configuration: {config_name}\n")
            f.write("-" * 40 + "\n")
            f.write(f"L1 Cache Hit Rate: {stats['l1_total_hit_rate']:.2f}%\n")
            f.write(f"L2 Cache Hit Rate: {stats['l2_hit_rate']:.2f}%\n")
            f.write(f"L1 Total Misses: {stats['l1_total_misses']:,}\n")
            f.write(f"L2 Total Misses: {stats['l2_misses']:,}\n")
            f.write(f"Simulation Time: {stats['sim_seconds']:.3f} seconds\n")
            f.write(f"Average CPI: {stats['avg_cpi']:.3f}\n")
            f.write(f"Total Instructions: {stats['sim_insts']:,}\n\n")
        
        # 性能排名
        f.write("Performance Rankings\n")
        f.write("-" * 30 + "\n")
        
        configs = list(all_stats.keys())
        
        # L1命中率排名
        l1_ranking = sorted(configs, key=lambda x: all_stats[x]['l1_total_hit_rate'], reverse=True)
        f.write("L1 Hit Rate Ranking: " + " > ".join(l1_ranking) + "\n")
        
        # L2命中率排名
        l2_ranking = sorted(configs, key=lambda x: all_stats[x]['l2_hit_rate'], reverse=True)
        f.write("L2 Hit Rate Ranking: " + " > ".join(l2_ranking) + "\n")
        
        # 执行速度排名（时间越短越好）
        speed_ranking = sorted(configs, key=lambda x: all_stats[x]['sim_seconds'])
        f.write("Execution Speed Ranking: " + " > ".join(speed_ranking) + "\n")
        
        # CPI排名（越低越好）
        cpi_ranking = sorted(configs, key=lambda x: all_stats[x]['avg_cpi'])
        f.write("CPI Performance Ranking: " + " > ".join(cpi_ranking) + "\n")
    
    print(f"📝 Performance report saved: {report_file}")

def main():
    """主函数"""
    print("📊 Analyzing MESI configuration performance data")
    print("=" * 50)
    
    # 配置目录
    config_dirs = {
        'Small Cache': 'results/small_cache',
        'Medium Cache': 'results/medium_cache', 
        'Large Cache': 'results/large_cache'
    }
    
    all_stats = {}
    
    # 解析所有配置的统计数据
    for config_name, result_dir in config_dirs.items():
        stats_file = os.path.join(result_dir, 'stats.txt')
        
        if os.path.exists(stats_file):
            print(f"📖 Parsing {config_name} data...")
            stats = parse_stats_file(stats_file)
            if stats:
                all_stats[config_name] = stats
                print(f"✅ {config_name} data parsed successfully")
            else:
                print(f"❌ {config_name} data parsing failed")
        else:
            print(f"❌ {config_name} stats file not found: {stats_file}")
    
    if not all_stats:
        print("❌ No valid statistics data found")
        print("Please run first: python3 run_all_configs.py")
        return
    
    # 生成比较图表
    print(f"\n📊 Generating performance comparison charts...")
    generate_comparison_charts(all_stats)
    
    # 生成总结报告
    print(f"\n📝 Generating performance report...")
    generate_summary_report(all_stats)
    
    print(f"\n🎉 Analysis complete! Results saved in 'results/' directory")

if __name__ == "__main__":
    main() 