# smbus integration test.  
# Test the smbus-cffi implementation using an arduino sketch that implements
# the smbus protocol using Wire.h. See test/test_sketch

from serial import Serial
from smbus import SMBus
import smbus
import time
import py


PORT = '/dev/ttyACM0'
ADDR = 0x04

# Commands
GETDATA = chr(254)
RESET = chr(255)

# Testcases
WRITE_QUICK          = chr(1)
READ_BYTE            = chr(2)
WRITE_BYTE           = chr(3)
READ_BYTE_DATA       = chr(4)
WRITE_BYTE_DATA      = chr(5)
READ_WORD_DATA       = chr(6)
WRITE_WORD_DATA      = chr(7)
PROCESS_CALL         = chr(8)
READ_BLOCK_DATA      = chr(9)
WRITE_BLOCK_DATA     = chr(10)
BLOCK_PROCESS_CALL   = chr(11)
READ_I2C_BLOCK_DATA  = chr(12)
WRITE_I2C_BLOCK_DATA = chr(13)

DELAY = 1

def command(testcase):
    def wrapper(f):
        f.testcase = testcase
        return f
    return wrapper


class BaseSMBusIntegration(object):
    def setup_method(self, meth):
        self.bus = SMBus(1)
        self.serial = Serial(PORT, 9600)
        self.serial.write(RESET)
        time.sleep(DELAY)
        self.serial.write(meth.testcase)
        time.sleep(DELAY)

    def getdata(self):
        self.serial.write(GETDATA)
        time.sleep(DELAY)
        return self.serial.readline().strip()


class TestSMBusIntegration(BaseSMBusIntegration):

    def setup_method(self, meth):
        BaseSMBusIntegration.setup_method(self, meth)
        self.bus._compat = True

    @command(WRITE_QUICK)
    def test_write_quick(self):
        self.bus.write_quick(ADDR)
        data = self.getdata()
        testcase, numbytes = data.split("#")
        assert testcase == WRITE_QUICK
        assert numbytes == chr(0)

    @command(READ_BYTE)
    def test_read_byte(self):
        self.serial.write('n')
        time.sleep(DELAY)
        byte = self.bus.read_byte(ADDR)
        'read ', byte
        data = self.getdata()
        assert data == READ_BYTE
        assert byte == ord('n')

    @command(READ_BYTE)
    def test_read_byte2(self):
        self.serial.write(chr(20))
        time.sleep(DELAY)
        byte = self.bus.read_byte(ADDR)
        'read ', byte
        data = self.getdata()
        assert data == READ_BYTE
        assert byte ==  20

    @command(WRITE_BYTE)
    def test_write_byte(self):
        byte = 31
        self.bus.write_byte(ADDR, byte)
        data = self.getdata()
        testcase, numbytes, bytes = data.split("#")
        assert testcase == WRITE_BYTE
        assert numbytes == chr(1)
        assert bytes == chr(31)

    @command(READ_BYTE_DATA)
    def test_read_byte_data(self):
        cmd = 17
        byte = self.bus.read_byte_data(ADDR, cmd)
        data = self.getdata()
        testcase, command, byte2 = data.split("#")
        assert testcase == READ_BYTE_DATA
        assert 17 == ord(command)
        assert byte == ord(byte2)

    @command(WRITE_BYTE_DATA)
    def test_write_byte_data(self):
        cmd = 17
        byte = 235
        self.bus.write_byte_data(ADDR, cmd, byte)
        time.sleep(DELAY)
        data = self.getdata()
        testcase, numbytes, command, byte2 = data.split("#")
        assert testcase == WRITE_BYTE_DATA
        assert 2 == ord(numbytes)
        assert cmd == ord(command)
        assert byte == ord(byte2)

    @command(READ_WORD_DATA)      
    def test_read_word_data(self):
        bytes = [1<<6, 1<<7]
        word = bytes[1] << 8 | bytes[0]
        cmd = 27
        self.serial.write(chr(bytes[0]) + chr(bytes[1]))
        time.sleep(DELAY)
        worddata = self.bus.read_word_data(ADDR, cmd)
        assert word == worddata
        data = self.getdata()
        testcase, cmd2, worddata2 = data.split("#")
        assert testcase == READ_WORD_DATA
        assert cmd == ord(cmd2)
        worddata2 = [ord(i) for i in worddata2]
        assert word == worddata2[1] << 8 | worddata2[0]

    @command(WRITE_WORD_DATA)
    def test_write_word_data(self):
        word = 0x40C8
        cmd = 13
        self.bus.write_word_data(ADDR, cmd, word)
        data = self.getdata()
        testcase, numbytes, cmd2, worddata = data.split("#")
        assert testcase == WRITE_WORD_DATA
        assert cmd == ord(cmd2) 
        assert 3 == ord(numbytes)
        worddata = [ord(i) for i in worddata]
        assert word == worddata[1] << 8 | worddata[0]

    @command(PROCESS_CALL)
    def test_process_call(self):
        word = 0xFADE
        cmd = 123
        result = self.bus.process_call(ADDR, cmd, word)
        testcase, cmd2, word2 = self.getdata().split("#")
        if not self.bus._compat: # in compat mode we do not get a return value
            assert result == 0xCAFE
        assert testcase == PROCESS_CALL
        assert cmd == ord(cmd2)
        assert word == ord(word2[0]) | ord(word2[1]) << 8


class TestCompatMode(BaseSMBusIntegration):
    @command(PROCESS_CALL)
    def test_process_call(self):
        word = 0xFADE
        cmd = 123
        result = self.bus.process_call(ADDR, cmd, word)
        testcase, cmd2, word2 = self.getdata().split("#")
        assert result is None
        assert testcase == PROCESS_CALL
        assert cmd == ord(cmd2)
        assert word == ord(word2[0]) | ord(word2[1]) << 8
