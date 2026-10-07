#include <tbb/tbb.h>
#include <iostream>
#include <vector>

int main(){
    std::cout << "tbb runtime version: " << TBB_runtime_version() << "\n";
    std::cout << "tbb runtime interface version: " << TBB_runtime_interface_version() << "\n";

    std::vector<int> values(128);
    tbb::parallel_for(size_t(0), values.size(), [&](size_t i) {
        values[i] = static_cast<int>(i * i);
    });

    tbb::concurrent_bounded_queue<int> queue;
    queue.set_capacity(1);
    for (size_t i = 0; i < values.size(); ++i) {
        queue.push(values[i]);
        int value = -1;
        queue.pop(value);
        if (value != static_cast<int>(i * i)) {
            return 1;
        }
    }
    return 0;
}
