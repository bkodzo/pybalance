"""
Setup script for building the C++ extension module.
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, Extension
import pybind11

ext_modules = [
    Pybind11Extension(
        "proxy_cpp",
        [
            "proxy_cpp.cpp",
        ],
        include_dirs=[
            # Additional include directories if needed
        ],
        language='c++',
        cxx_std=17,
    ),
]

setup(
    name="pbalance",
    version="1.0.0",
    author="PyBalance",
    description="C++ extension for high-performance byte operations",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)

