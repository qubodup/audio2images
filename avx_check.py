import ctypes
import os
import platform
import subprocess
import sys

def has_avx():
    """Check for AVX support using CPUID instruction on Windows"""
    # This only works on Intel/AMD x86 CPUs
    if platform.machine().lower() not in ['x86_64', 'amd64', 'i386', 'i686']:
        return False

    try:
        import cpuinfo
    except ImportError:
        print("Installing py-cpuinfo...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "py-cpuinfo"])
        import cpuinfo

    info = cpuinfo.get_cpu_info()
    flags = info.get("flags", [])
    return "avx" in flags

def test_import_numpy():
    try:
        import numpy
        print(f"NICE Successfully imported NumPy version {numpy.__version__}")
    except Exception as e:
        print("X NumPy failed to import.")
        print(e)

if __name__ == "__main__":
    print("SEARCH Checking AVX support...")

    if not has_avx():
        print("\nWARN This CPU does NOT support AVX.")
        print("FAIL Importing recent versions of NumPy may silently crash.")
        print("INFO Recommendation: Use NumPy <= 1.19.5 for compatibility.\n")
    else:
        print("OK AVX is supported on this CPU.\n")

    print("TEST Testing NumPy import...")
    test_import_numpy()
