// File: cnn_test.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INPUT_SIZE 32
#define FILTER_SIZE 3
#define OUTPUT_SIZE (INPUT_SIZE - FILTER_SIZE + 1)
#define NUM_FILTERS 16

// 模擬CNN層的資料結構
typedef struct {
    float input[INPUT_SIZE][INPUT_SIZE];
    float filters[NUM_FILTERS][FILTER_SIZE][FILTER_SIZE];
    float output[NUM_FILTERS][OUTPUT_SIZE][OUTPUT_SIZE];
    float bias[NUM_FILTERS];
} cnn_layer_t;

// 初始化輸入資料
void init_input_data(cnn_layer_t* layer) {
    printf("Initializing CNN input data...\n");
    for(int i = 0; i < INPUT_SIZE; i++) {
        for(int j = 0; j < INPUT_SIZE; j++) {
            layer->input[i][j] = (float)(i * INPUT_SIZE + j) / 1000.0f;
        }
    }
}

// 初始化濾波器權重
void init_filters(cnn_layer_t* layer) {
    printf("Initializing CNN filters...\n");
    for(int f = 0; f < NUM_FILTERS; f++) {
        layer->bias[f] = 0.1f * f;
        for(int i = 0; i < FILTER_SIZE; i++) {
            for(int j = 0; j < FILTER_SIZE; j++) {
                layer->filters[f][i][j] = (float)(f + i + j) / 100.0f;
            }
        }
    }
}

// 卷積運算 - 產生大量記憶體存取以觸發MESI協議
void convolution_layer(cnn_layer_t* layer) {
    printf("Performing CNN convolution...\n");
    
    for(int f = 0; f < NUM_FILTERS; f++) {
        for(int out_i = 0; out_i < OUTPUT_SIZE; out_i++) {
            for(int out_j = 0; out_j < OUTPUT_SIZE; out_j++) {
                float sum = layer->bias[f];
                
                // 卷積運算 - 大量記憶體讀取
                for(int fi = 0; fi < FILTER_SIZE; fi++) {
                    for(int fj = 0; fj < FILTER_SIZE; fj++) {
                        int input_i = out_i + fi;
                        int input_j = out_j + fj;
                        sum += layer->input[input_i][input_j] * 
                               layer->filters[f][fi][fj];
                    }
                }
                
                // ReLU激活函數
                layer->output[f][out_i][out_j] = (sum > 0) ? sum : 0;
            }
        }
    }
}

// 池化層 - 進一步的記憶體存取模式
void pooling_layer(cnn_layer_t* layer) {
    printf("Performing max pooling...\n");
    
    for(int f = 0; f < NUM_FILTERS; f++) {
        for(int i = 0; i < OUTPUT_SIZE - 1; i += 2) {
            for(int j = 0; j < OUTPUT_SIZE - 1; j += 2) {
                float max_val = layer->output[f][i][j];
                
                // 尋找2x2區域的最大值
                for(int pi = 0; pi < 2; pi++) {
                    for(int pj = 0; pj < 2; pj++) {
                        if(i + pi < OUTPUT_SIZE && j + pj < OUTPUT_SIZE) {
                            float val = layer->output[f][i + pi][j + pj];
                            if(val > max_val) max_val = val;
                        }
                    }
                }
                
                // 寫回結果 - 觸發cache寫入
                layer->output[f][i/2][j/2] = max_val;
            }
        }
    }
}

// 計算輸出統計 - 驗證計算正確性
void compute_statistics(cnn_layer_t* layer) {
    float total_sum = 0.0f;
    float max_val = -1000.0f;
    float min_val = 1000.0f;
    int total_elements = 0;
    
    printf("Computing output statistics...\n");
    
    for(int f = 0; f < NUM_FILTERS; f++) {
        for(int i = 0; i < OUTPUT_SIZE; i++) {
            for(int j = 0; j < OUTPUT_SIZE; j++) {
                float val = layer->output[f][i][j];
                total_sum += val;
                if(val > max_val) max_val = val;
                if(val < min_val) min_val = val;
                total_elements++;
            }
        }
    }
    
    printf("CNN Results:\n");
    printf("  Total elements: %d\n", total_elements);
    printf("  Sum: %.6f\n", total_sum);
    printf("  Average: %.6f\n", total_sum / total_elements);
    printf("  Max: %.6f\n", max_val);
    printf("  Min: %.6f\n", min_val);
}

// 記憶體密集型測試 - 模擬多核心存取
void memory_stress_test() {
    printf("Running memory stress test for MESI protocol...\n");
    
    const int ARRAY_SIZE = 1024;
    volatile int* shared_data = malloc(ARRAY_SIZE * sizeof(int));
    
    if(!shared_data) {
        printf("Memory allocation failed!\n");
        return;
    }
    
    // 模擬多核心競爭存取
    for(int iteration = 0; iteration < 100; iteration++) {
        // 寫入階段 - 觸發Modified狀態
        for(int i = 0; i < ARRAY_SIZE; i++) {
            shared_data[i] = iteration * i;
        }
        
        // 讀取階段 - 觸發Shared狀態
        int sum = 0;
        for(int i = 0; i < ARRAY_SIZE; i++) {
            sum += shared_data[i];
        }
        
        // 隨機存取模式 - 觸發cache miss
        for(int i = 0; i < 100; i++) {
            int idx = (iteration * 7 + i * 13) % ARRAY_SIZE;
            shared_data[idx] = sum + i;
        }
    }
    
    free((void*)shared_data);
    printf("Memory stress test completed.\n");
}

int main() {
    printf("=== CNN MESI Protocol Test Program ===\n");
    printf("Testing cache coherency with CNN workload\n\n");
    
    // 分配CNN層結構
    cnn_layer_t* layer = malloc(sizeof(cnn_layer_t));
    if(!layer) {
        printf("Failed to allocate CNN layer!\n");
        return 1;
    }
    
    // 執行CNN運算流程
    init_input_data(layer);
    init_filters(layer);
    convolution_layer(layer);
    pooling_layer(layer);
    compute_statistics(layer);
    
    // 執行記憶體壓力測試
    memory_stress_test();
    
    // 清理資源
    free(layer);
    
    printf("\n=== CNN MESI Test Completed Successfully ===\n");
    return 0;
}

