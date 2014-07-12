from smbus import SMBus


class SMBusProxy(object):
    def __init__(self, bus=-1):
        self.called = False
        self.passed_args = ()
        self.smbus = SMBus()
        if bus != -1:
            self.open(bus)

    def open(self, *args):
        self.called = True
        self.passed_args = args

    def __getattr__(self, name, *args, **kwargs):
        return getattr(self.smbus, name, *args, **kwargs)


class TestSMBus_init(object):

    def test_init_with_arg_tries_to_open(self):
        bus = SMBusProxy(12)

        assert bus.called
        assert bus.passed_args == (12,)

    def test_init_does_nothing_by_default(self):
        bus = SMBusProxy()
        if hasattr(bus, '_fd'):
            assert bus._fd == -1
            assert bus._addr == -1
            assert bus._pec == 0
        assert not bus.called


def test_list_to_smbus_data():
    from smbus import ffi, list_to_smbus_data
    lst = range(10)
    data = ffi.new("union i2c_smbus_data *")
    list_to_smbus_data(data, lst)
    assert data.block[0] == 10
    for i in lst:
        assert data.block[i + 1] == i


def test_smbus_data_to_list():
    from smbus import ffi, list_to_smbus_data, smbus_data_to_list
    lst = range(10)
    data = ffi.new("union i2c_smbus_data *")
    list_to_smbus_data(data, lst)
    assert smbus_data_to_list(data) == range(10)
