try:
    import cffi.verifier
    cffi.verifier.cleanup_tmpdir()
except ImportError:
    pass
