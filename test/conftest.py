import os


def pytest_configure(config):
    from smbus_cffi_build import ffi
    target = os.path.join(os.path.dirname(__file__), '..', 'smbus')
    ffi.compile(tmpdir=target)
