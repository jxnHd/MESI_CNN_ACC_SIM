# File: src/cnn_accelerator/CNNAccelerator.py
from m5.params import *
from m5.objects.ClockedObject import ClockedObject

class CNNAccelerator(ClockedObject):  # 必須繼承ClockedObject
    type = 'CNNAccelerator'
    cxx_header = "cnn_accelerator/cnn_accelerator.hh"
    cxx_class = "gem5::CNNAccelerator"
    
    cache_port = RequestPort("Cache port")
    dma_port = RequestPort("DMA port")

