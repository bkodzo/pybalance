# Building the C++ Extension

The C++ extension is **optional** but provides significant performance improvements for high-throughput scenarios.

## Prerequisites

- Python 3.7+
- C++ compiler (GCC, Clang, or MSVC)
- pip

## Quick Build

```bash
# Install dependencies
pip3 install pybind11 setuptools

# Build extension
make install

# Or manually:
python3 setup.py build_ext --inplace
```

## Verify Installation

```bash
make test
# Should output: "C++ extension loaded successfully"
```

## Performance Benefits

The C++ extension provides:

1. **Fast Byte Copying**: 2-3x faster for large data transfers (>4KB)
2. **Optimized Memory Operations**: Better cache locality
3. **Fast HTTP Parsing**: Header parsing without full string decoding
4. **Zero-Copy Operations**: Where possible, avoids unnecessary copies

## Platform-Specific Notes

### Linux/macOS
- Uses standard GCC/Clang
- Extension builds as `.so` file

### Windows
- Requires Visual Studio Build Tools or MinGW
- Extension builds as `.pyd` file

## Troubleshooting

**ImportError when importing proxy_cpp:**
- Make sure you built the extension: `make install`
- Check that `proxy_cpp*.so` (or `.pyd` on Windows) exists in the project directory
- Verify Python version matches the one used to build

**Build errors:**
- Ensure pybind11 is installed: `pip3 install pybind11`
- Check that you have a C++ compiler installed
- On macOS, you may need: `xcode-select --install`

## Using Without C++ Extension

The load balancer works perfectly fine without the C++ extension. It will:
- Automatically detect if the extension is available
- Use it if present for performance boost
- Gracefully fall back to pure Python if not available

No code changes needed - it's completely transparent!

