# File: config/cache_config.py
from m5.objects import Cache

class L1Cache(Cache):
    """基本L1 Cache配置"""
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    
    def __init__(self, options=None):
        super(L1Cache, self).__init__()
        pass

class L1ICache(L1Cache):
    """L1指令Cache"""
    size = '16kB'
    
    def __init__(self, options=None):
        super(L1ICache, self).__init__(options)
        if options and hasattr(options, 'l1i_size'):
            self.size = options.l1i_size
    
    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port
    
    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

class L1DCache(L1Cache):
    """L1資料Cache"""
    size = '32kB'
    
    def __init__(self, options=None):
        super(L1DCache, self).__init__(options)
        if options and hasattr(options, 'l1d_size'):
            self.size = options.l1d_size
    
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port
    
    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

class L2Cache(Cache):
    """L2 Cache配置"""
    size = '256kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    
    def __init__(self, options=None):
        super(L2Cache, self).__init__()
        if options and hasattr(options, 'l2_size'):
            self.size = options.l2_size
    
    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports
    
    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports

