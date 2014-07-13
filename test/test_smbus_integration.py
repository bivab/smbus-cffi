# smbus integration test.
# Test the smbus-cffi implementation using an arduino sketch that implements
# the smbus protocol using Wire.h. See test/test_sketch

from serial import Serial
from smbus import SMBus
import time
import py


PORT = '/dev/ttyACM0'
ADDR = 0x04
BUS = 1

# Commands
GETDATA = chr(254)
RESET = chr(255)

# Testcases
WRITE_QUICK = 1
READ_BYTE = 2
WRITE_BYTE = 3
READ_BYTE_DATA = 4
WRITE_BYTE_DATA = 5
READ_WORD_DATA = 6
WRITE_WORD_DATA = 7
PROCESS_CALL = 8
READ_BLOCK_DATA = 9
WRITE_BLOCK_DATA = 10
BLOCK_PROCESS_CALL = 11
READ_I2C_BLOCK_DATA = 12
WRITE_I2C_BLOCK_DATA = 13

DELAY = 1

i2c_features = {}
i2c_feature_map = {
    'SMBus Quick Command': WRITE_QUICK,
    'SMBus Send Byte': WRITE_BYTE,
    'SMBus Receive Byte': READ_BYTE,
    'SMBus Write Byte': WRITE_BYTE_DATA,
    'SMBus Read Byte': READ_BYTE_DATA,
    'SMBus Write Word': WRITE_WORD_DATA,
    'SMBus Read Word': READ_WORD_DATA,
    'SMBus Process Call': PROCESS_CALL,
    'SMBus Block Write': WRITE_BLOCK_DATA,
    'SMBus Block Read': READ_BLOCK_DATA,
    'SMBus Block Process Call': BLOCK_PROCESS_CALL,
    'SMBus PEC': -1,
    'I2C Block Write': WRITE_I2C_BLOCK_DATA,
    'I2C Block Read': READ_I2C_BLOCK_DATA,
}


def get_i2c_features():
    import subprocess
    try:
        output = subprocess.Popen(["i2cdetect", "-F", "1"],
                                  stdout=subprocess.PIPE).communicate()[0]
        return output.split('\n')[1:]
    except OSError:
        py.test.skip("Requires i2cdetect command")


def detect_i2c_features():
    features = get_i2c_features()
    for line in features:
        if line == '':
            continue
        for n in ('yes', 'no'):
            i = line.find(n)
            if i == -1:
                continue
            key = line[0:i - 1].strip()
            key = i2c_feature_map.get(key, -1)
            i2c_features[key] = True if n == 'yes' else False
            break
        else:
            import pdb
            pdb.set_trace()

detect_i2c_features()
del detect_i2c_features


def command(testcase):
    def wrapper(f):
        f.testcase = testcase
        return f
    return wrapper


def pytest_funcarg__smbus(*args, **kwargs):
    return SMBus(BUS)


def test_open():
    bus = SMBus()
    py.test.raises(IOError, 'bus.open(-13)')

    bus.open(BUS)  # does not raise

    if hasattr(bus, '_fd'):
        assert bus._fd != -1


def test_write_quick(smbus):
    py.test.raises(TypeError, "smbus.write_quick('a')")
    py.test.raises(IOError, "smbus.write_quick(44)")
    smbus.write_quick(ADDR)


def test_pec(smbus):
    assert not smbus.pec  # default value
    smbus.pec = None
    assert not smbus.pec
    smbus.pec = 5
    assert smbus.pec
    smbus.pec = True
    assert smbus.pec


class BaseSMBusIntegration(object):
    def setup_method(self, meth):
        if not i2c_features[meth.testcase]:
            py.test.skip("smbus feature not supported")
        self.bus = SMBus(BUS)
        self.serial = Serial(PORT, 9600)
        self.serial.write(RESET)
        time.sleep(DELAY)
        self.serial.write(chr(meth.testcase))
        time.sleep(DELAY)

    def getdata(self):
        self.serial.write(GETDATA)
        time.sleep(DELAY)
        return self.serial.readline().strip()


class TestSMBusIntegration(BaseSMBusIntegration):

    def setup_method(self, meth):
        BaseSMBusIntegration.setup_method(self, meth)
        if hasattr(self.bus, '_compat'):
            self.bus._compat = True

    @command(WRITE_QUICK)
    def test_write_quick(self):
        self.bus.write_quick(ADDR)
        data = self.getdata()
        testcase, numbytes = [int(i) for i in data.split("#")]
        assert WRITE_QUICK == testcase
        assert 0 == numbytes

    @command(READ_BYTE)
    def test_read_byte(self):
        self.serial.write('n')
        time.sleep(DELAY)
        byte = self.bus.read_byte(ADDR)
        'read ', byte
        data = int(self.getdata())
        assert data == READ_BYTE
        assert byte == ord('n')

    @command(READ_BYTE)
    def test_read_byte2(self):
        self.serial.write(chr(20))
        time.sleep(DELAY)
        byte = self.bus.read_byte(ADDR)
        'read ', byte
        data = int(self.getdata())
        assert data == READ_BYTE
        assert byte == 20

    @command(WRITE_BYTE)
    def test_write_byte(self):
        byte = 31
        self.bus.write_byte(ADDR, byte)
        data = self.getdata()
        testcase, numbytes, bytes = [int(i) for i in data.split("#")]
        assert testcase == WRITE_BYTE
        assert numbytes == 1
        assert bytes == 31

    @command(READ_BYTE_DATA)
    def test_read_byte_data(self):
        cmd = 17
        byte = self.bus.read_byte_data(ADDR, cmd)
        data = self.getdata()
        testcase, command, byte2 = [int(i) for i in data.split("#")]
        assert testcase == READ_BYTE_DATA
        assert 17 == command
        assert byte == byte2

    @command(WRITE_BYTE_DATA)
    def test_write_byte_data(self):
        cmd = 17
        byte = 235
        self.bus.write_byte_data(ADDR, cmd, byte)
        time.sleep(DELAY)
        data = self.getdata()
        testcase, numbytes, command, byte2 = [int(i) for i in data.split("#")]
        assert testcase == WRITE_BYTE_DATA
        assert 2 == numbytes
        assert cmd == command
        assert byte == byte2

    @command(READ_WORD_DATA)
    def test_read_word_data(self):
        bytes = [1 << 6, 1 << 7]
        word = bytes[1] << 8 | bytes[0]
        cmd = 27
        self.serial.write(chr(bytes[0]) + chr(bytes[1]))
        time.sleep(DELAY)
        worddata = self.bus.read_word_data(ADDR, cmd)
        assert word == worddata
        data = self.getdata()
        testcase, cmd2, worddata2 = data.split("#")
        assert int(testcase) == READ_WORD_DATA
        assert cmd == int(cmd2)
        worddata2 = [ord(i) for i in worddata2]
        assert word == worddata2[1] << 8 | worddata2[0]

    @command(WRITE_WORD_DATA)
    def test_write_word_data(self):
        word = 0x40C8
        cmd = 13
        self.bus.write_word_data(ADDR, cmd, word)
        data = self.getdata()
        testcase, numbytes, reg, worddata = data.split("#")
        assert int(testcase) == WRITE_WORD_DATA
        assert int(reg) == cmd
        assert int(numbytes) == 3
        worddata = [int(i) for i in worddata.split('|')]
        assert word == worddata[1] << 8 | worddata[0]

    @command(PROCESS_CALL)
    def test_process_call(self):
        word = 0xFADE
        cmd = 123
        result = self.bus.process_call(ADDR, cmd, word)
        data = self.getdata()
        testcase, cmd2, byte1, byte2 = [int(i) for i in data.split("#")]
        if hasattr(self.bus, '_compat') and not self.bus._compat: # in compat mode we do not get a return value
            assert result == 0xCAFE
        assert testcase == PROCESS_CALL
        assert cmd == cmd2
        assert word == byte1 | byte2 << 8

    @command(READ_BLOCK_DATA)
    def test_read_block_data(self):
        cmd = 217
        self.bus.read_block_data(ADDR, cmd)
        data = self.getdata()
        testcase, register = [int(i) for i in data.split("#")]
        assert testcase == READ_BLOCK_DATA
        assert cmd == register
        assert 0, 'incomplete'

    @command(BLOCK_PROCESS_CALL)
    def test_block_process_call(self):
        assert 0, 'incomplete'

    @command(WRITE_BLOCK_DATA)
    def test_write_block_data(self):
        data = range(65, 86)
        cmd = 0x7
        self.bus.write_block_data(ADDR, cmd, data)
        d = self.getdata()
        testcase, numbytes, reg, blockdata = d.split("#")
        assert WRITE_BLOCK_DATA == int(testcase)
        assert cmd == int(reg)
        blockdata = [int(i) for i in blockdata.split('|')]
        assert blockdata == [len(data)] + data

    @command(READ_I2C_BLOCK_DATA)
    def test_read_i2c_block_data(self):
        cmd = 217
        exp = range(100, 132)
        blockdata = self.bus.read_i2c_block_data(ADDR, cmd)
        data = self.getdata()
        testcase, reg, numbytes = [int(i) for i in data.split("#")]
        assert READ_I2C_BLOCK_DATA == testcase
        assert cmd == reg
        assert 1 == numbytes
        assert exp == blockdata

    @command(WRITE_I2C_BLOCK_DATA)
    def test_write_i2c_block_data(self):
        cmd = 217
        exp = range(100, 131)
        self.bus.write_i2c_block_data(ADDR, cmd, exp)
        data = self.getdata()
        testcase, numbytes, reg, blockdata = [i for i in data.split("#")]
        blockdata = [int(i) for i in blockdata.split('|')]
        assert WRITE_I2C_BLOCK_DATA == int(testcase)
        assert cmd == int(reg)
        assert len(exp) + 1 == int(numbytes)
        assert exp == blockdata


class TestCompatMode(BaseSMBusIntegration):
    @command(PROCESS_CALL)
    def test_process_call(self):
        word = 0xFADE
        cmd = 123
        result = self.bus.process_call(ADDR, cmd, word)
        data = self.getdata()
        testcase, reg, byte1, byte2 = [int(i) for i in data.split("#")]
        # in compat mode we do not get a return value
        assert result is None
        assert testcase == PROCESS_CALL
        assert cmd == reg
        assert word == byte1 | byte2 << 8
