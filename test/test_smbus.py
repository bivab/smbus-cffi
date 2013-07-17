from smbus import SMBus
import py

class TestSMBus_init(object):
    called = False
    passed_args = None
    #tmp = None

    def setup_method(self, *args):
        self.tmp = SMBus.open
        def open_helper(*args):
            self.called = True
            self.passed_args = args
        SMBus.open = open_helper

    def teardown_method(self, *args):
        SMBus.open  = self.tmp

    def test_init_with_arg_tries_to_open(self):
        bus = SMBus(12)

        assert self.called
        assert self.passed_args == (bus, 12)

    def test_init_does_nothing_by_default(self):
        bus = SMBus()

        assert bus.fd == -1
        assert bus.addr == -1
        assert bus.pec == 0
        assert not self.called


def test_open():
    b = SMBus()
    py.test.raises(IOError, 'b.open(-13)')

    b.open(1)
    assert b.fd != -1

