# Makefile for building C++ extension

.PHONY: build install clean test

build:
	python3 setup.py build_ext --inplace

install:
	pip3 install pybind11
	python3 setup.py build_ext --inplace

clean:
	rm -rf build/
	rm -f proxy_cpp*.so proxy_cpp*.pyd
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

test:
	python3 -c "import proxy_cpp; print('C++ extension loaded successfully')"

