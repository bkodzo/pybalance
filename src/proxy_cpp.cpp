/*
 * C++ extension for high-performance byte operations
 * Optimizes data transfer between client and backend sockets
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <cstring>
#include <vector>
#include <algorithm>

namespace py = pybind11;

/**
 * Copy bytes using memcpy for maximum performance on large transfers
 */
std::vector<uint8_t> fast_copy(const std::vector<uint8_t>& data) {
    std::vector<uint8_t> result(data.size());
    std::memcpy(result.data(), data.data(), data.size());
    return result;
}

/**
 * Return reference to avoid copying when peeking at data
 */
const std::vector<uint8_t>& buffer_view(const std::vector<uint8_t>& data) {
    return data;
}

/**
 * Process chunks in batches for better cache locality
 */
std::vector<std::vector<uint8_t>> process_chunks(
    const std::vector<uint8_t>& data,
    size_t chunk_size
) {
    std::vector<std::vector<uint8_t>> chunks;
    size_t offset = 0;
    
    while (offset < data.size()) {
        size_t current_chunk_size = std::min(chunk_size, data.size() - offset);
        std::vector<uint8_t> chunk(current_chunk_size);
        std::memcpy(chunk.data(), data.data() + offset, current_chunk_size);
        chunks.push_back(std::move(chunk));
        offset += current_chunk_size;
    }
    
    return chunks;
}

/**
 * Parse HTTP header to extract method and path
 */
std::pair<std::string, std::string> parse_http_header(
    const std::vector<uint8_t>& data
) {
    std::string method, path;
    
    size_t method_end = 0;
    for (size_t i = 0; i < data.size() && i < 20; ++i) {
        if (data[i] == ' ') {
            method_end = i;
            break;
        }
    }
    
    if (method_end > 0) {
        method = std::string(
            reinterpret_cast<const char*>(data.data()),
            method_end
        );
        
        size_t path_start = method_end + 1;
        size_t path_end = path_start;
        for (size_t i = path_start; i < data.size() && i < path_start + 200; ++i) {
            if (data[i] == ' ' || data[i] == '\r' || data[i] == '\n') {
                path_end = i;
                break;
            }
        }
        
        if (path_end > path_start) {
            path = std::string(
                reinterpret_cast<const char*>(data.data() + path_start),
                path_end - path_start
            );
        }
    }
    
    return {method, path};
}

/**
 * Concatenate buffers efficiently by pre-allocating result
 */
std::vector<uint8_t> concat_buffers(
    const std::vector<std::vector<uint8_t>>& buffers
) {
    size_t total_size = 0;
    for (const auto& buf : buffers) {
        total_size += buf.size();
    }
    
    std::vector<uint8_t> result(total_size);
    size_t offset = 0;
    
    for (const auto& buf : buffers) {
        std::memcpy(result.data() + offset, buf.data(), buf.size());
        offset += buf.size();
    }
    
    return result;
}

PYBIND11_MODULE(proxy_cpp, m) {
    m.doc() = "High-performance C++ extension for PyBalance byte operations";
    
    m.def("fast_copy", &fast_copy, "Fast byte copy with optimized memory handling");
    m.def("buffer_view", &buffer_view, "Zero-copy buffer view");
    m.def("process_chunks", &process_chunks, 
          "Process data into optimized chunks",
          py::arg("data"), py::arg("chunk_size"));
    m.def("parse_http_header", &parse_http_header,
          "Fast HTTP header parsing (method and path)");
    m.def("concat_buffers", &concat_buffers,
          "Memory-efficient buffer concatenation");
}

