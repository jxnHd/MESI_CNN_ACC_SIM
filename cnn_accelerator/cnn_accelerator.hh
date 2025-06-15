#ifndef __CNN_ACCELERATOR_HH__
#define __CNN_ACCELERATOR_HH__

#include "mem/port.hh"
#include "params/CNNAccelerator.hh"
#include "sim/clocked_object.hh"

namespace gem5 {

class CNNAccelerator : public ClockedObject
{
  private:
    // 自定義請求端口類別
    class AccelRequestPort : public RequestPort
    {
      private:
        CNNAccelerator *owner;

      public:
        AccelRequestPort(const std::string& name, CNNAccelerator *owner)
          : RequestPort(name), owner(owner) {}

      protected:
        // 必須實現的純虛函數
        bool recvTimingResp(PacketPtr pkt) override { return true; }
        void recvReqRetry() override {}
        void recvRangeChange() override {}
    };

  public:
    //typedef CNNAcceleratorParams Params;
    AccelRequestPort cache_port;
    AccelRequestPort dma_port;

    CNNAccelerator(const CNNAcceleratorParams &p);
    
    // 关键修正：添加getPort方法
    Port &getPort(const std::string &if_name, PortID idx = InvalidPortID) override;
    
    void printMESIState(Addr addr, int state);
    
    // 新增：MESI協議模擬方法
    void simulateMESIStates();

  private:
    const char* stateToString(int state);
};

} // namespace gem5

#endif // __CNN_ACCELERATOR_HH__
