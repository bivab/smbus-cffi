def pytest_configure(config):
    from smbus_cffi_build import ffi
    ffi.compile()
