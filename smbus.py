# smbus.py - cffi based python bindings for SMBus based on smbusmodule.c
#
# smbusmodule.c - Python bindings for Linux SMBus access through i2c-dev
# Copyright (C) 2005-2007 Mark M. Hoffman <mhoffman@lightlink.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""This module defines an object type that allows SMBus transactions
on hosts running the Linux kernel.  The host kernel must have I2C
support, I2C device interface support, and a bus adapter driver.
All of these can be either built-in to the kernel, or loaded from
modules.

Because the I2C device interface is opened R/W, users of this
module usually must have root permissions."""

from util import validate
MAXPATH=16

from cffi import FFI
ffi = FFI()
ffi.cdef("""
#define O_RDWR ...
int open(const char *pathname, int flags, int mode);
int close(int fd);
int ioctl(int d, int request, ...);
""")
C = ffi.verify("""
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/types.h>
""")

smbus_ffi = FFI()
smbus_ffi.cdef("""
typedef unsigned char __u8;
typedef int32_t __s32;
typedef unsigned short int __u16;

#define I2C_SLAVE ...

/* smbus_access read or write markers */
#define I2C_SMBUS_READ  ...
#define I2C_SMBUS_WRITE ...

/* SMBus transaction types (size parameter in the above functions) 
   Note: these no longer correspond to the (arbitrary) PIIX4 internal codes! */
#define I2C_SMBUS_QUICK             ...
#define I2C_SMBUS_BYTE              ...
#define I2C_SMBUS_BYTE_DATA         ...
#define I2C_SMBUS_WORD_DATA         ...
#define I2C_SMBUS_PROC_CALL         ...
#define I2C_SMBUS_BLOCK_DATA        ...
#define I2C_SMBUS_I2C_BLOCK_BROKEN  ...
#define I2C_SMBUS_BLOCK_PROC_CALL   ...   /* SMBus 2.0 */
#define I2C_SMBUS_I2C_BLOCK_DATA    ...

/* 
 * Data for SMBus Messages 
 */
//#define I2C_SMBUS_BLOCK_MAX	32	/* As specified in SMBus standard */	
union i2c_smbus_data {
	__u8 byte;
	__u16 word;
	__u8 block[34]; /* block[0] is used for length */
	                                            /* and one more for PEC */
};


static inline __s32 i2c_smbus_access(int file, char read_write, __u8 command, int size, union i2c_smbus_data *data);

static inline __s32 i2c_smbus_write_quick(int file, __u8 value);

static inline __s32 i2c_smbus_read_byte(int file);
static inline __s32 i2c_smbus_write_byte(int file, __u8 value);

static inline __s32 i2c_smbus_read_byte_data(int file, __u8 command);
static inline __s32 i2c_smbus_write_byte_data(int file, __u8 command, __u8 value);

static inline __s32 i2c_smbus_read_word_data(int file, __u8 command);
static inline __s32 i2c_smbus_write_word_data(int file, __u8 command, __u16 value);

static inline __s32 i2c_smbus_process_call(int file, __u8 command, __u16 value);

//static inline __s32 i2c_smbus_read_block_data(int file, __u8 command, __u8 *values)
//static inline __s32 i2c_smbus_write_block_data(int file, __u8 command, __u8 length, const __u8 *values)
""")
SMBUS = smbus_ffi.verify("""
#include <sys/types.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
""")

class SMBus(object):
    """Return a new SMBus object that is (optionally) connected to the
    specified I2C device interface."""
    _fd = -1
    _addr = -1
    _pec = 0

    def __init__(self, bus=-1):
        if bus >= 0:
            self.open(bus)

    def close(self):
        """Disconnects the object from the bus."""
        if self._fd != -1 and C.close(self._fd):
            raise IOError
        self._fd = -1
        self._addr = -1
        self._pec = 0

    def dealloc(self):
        self.close()

    def open(self, bus):
        """Connects the object to the specified SMBus."""
        bus = int(bus)
        path = "/dev/i2c-%d" % (bus,)
        if len(path) >= MAXPATH:
                raise OverflowError("Bus number is invalid.")

        self._fd = C.open(path, C.O_RDWR, 0)
        if self._fd == -1:
            raise IOError(ffi.errno)

    def _set_addr(self, addr):
        """private helper function, 0 => success, !0 => error"""
        ret = 0
        if self._addr != addr:
            ret = C.ioctl(self._fd, SMBUS.I2C_SLAVE, ffi.cast("int", addr))
            self._addr = addr
        if ret != 0:
            raise IOError(ffi.errno)
        return ret

    @validate(addr=int)
    def write_quick(self, addr):
        """Perform SMBus Quick transaction."""
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_quick(self._fd, SMBUS.I2C_SMBUS_WRITE) != 0:
            raise IOError(ffi.errno)

    @validate(addr=int)
    def read_byte(self, addr):
        """Perform SMBus Write Byte transaction."""
        self._set_addr(addr)
        result = SMBUS.i2c_smbus_read_byte(self._fd)
        if result == -1:
            raise IOError(ffi.errno)
        return result

    @validate(addr=int, val=int)
    def write_byte(self, addr, val):
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_byte(self._fd, ffi.cast("unsigned char", val)) == -1:
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int)
    def read_byte_data(self, addr, cmd):
        self._set_addr(addr)
        result = SMBUS.i2c_smbus_read_byte_data(self._fd, ffi.cast("unsigned char", cmd))
        if result == -1:
            raise IOError(ffi.errno)
        return result

    @validate(addr=int, cmd=int, val=int)
    def write_byte_data(self, addr, cmd, val):
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_byte_data(self._fd, 
            ffi.cast("unsigned char", cmd),
            ffi.cast("unsigned char", val)) == -1:
            raise IOError(ffi.errno)


    @validate(addr=int, cmd=int)
    def read_word_data(self, addr, cmd):
        self._set_addr(addr)
        result = SMBUS.i2c_smbus_read_word_data(self._fd, ffi.cast("unsigned char", cmd))
        if result == -1:
            raise IOError(ffi.errno)
        return result

    @validate(addr=int, cmd=int, val=int)
    def write_word_data(self, addr, cmd, val):
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_word_data(self._fd,
            ffi.cast("unsigned char", cmd),
            ffi.cast("unsigned short", val)) == -1:
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int, val=int)
    def process_call(self, addr, cmd, val):
        self._set_addr(addr)
        if SMBUS.i2c_smbus_process_call(self._fd,
            ffi.cast("unsigned char", cmd),
            ffi.cast("unsigned char", val)) == -1:
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int)
    def read_block_data(self, addr, cmd):
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data")
        if SMBUS.i2c_smbus_access(self._fd, SMBUS.I2C_SMBUS_READ,
                                  ffi.cast("unsigned char", cmd),
                                  SMBUS.I2C_SMBUS_BLOCK_DATA,
                                  data):
            raise IOError(ffi.errno)
        return smbus_data_to_list(data.block)
        
    @validate(addr=int, cmd=int, vals=list)
    def write_block_data(self, addr, cmd, vals):
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data")
        list_to_smbus_data(data, vals)  
        if SMBUS.i2c_smbus_access(self._fd, SMBUS.I2C_SMBUS_WRITE, 
                                  ffi.cast("unsigned char", cmd), 
                                  SMBUS.I2C_SMBUS_BLOCK_DATA,
                                  data):
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int, len=int)
    def block_process_call(self, addr, cmd, vals):
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data")
        list_to_smbus_data(data, vals)  
        if SMBUS.i2c_smbus_access(self._fd, SMBUS.I2C_SMBUS_WRITE,
                                  ffi.cast("unsigned char", cmd), 
                                  SMBUS.I2C_SMBUS_BLOCK_PROC_CALL,
                                  data):
            raise IOError(ffi.errno)
        return smbus_data_to_list(data.block)

    @validate(addr=int, cmd=int, len=list)
    def read_i2c_block_data(addr, cmd, len=32):
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data")
        data.block[0] = len
        arg = SMBUS.I2C_SMBUS_I2C_BLOCK_BROKEN if len == 32 else SMBUS.I2C_SMBUS_I2C_BLOCK_DATA
        if SMBUS.i2c_smbus_access(self._fd,
                                  SMBUS.I2C_SMBUS_READ,
                                  ffi.cast("unsigned char", cmd), 
                                  arg, data):
            raise IOError(ffi.errno)
        return smbus_data_to_list(data.block)

    @validate(addr=int, cmd=int, vals=list)
    def write_i2c_block_data(addr, cmd, vals):
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data")
        list_to_smbus_data(data, vals)  
        if SMBUS.i2c_smbus_access(self._fd, SMBUS.I2C_SMBUS_WRITE,
                                  ffi.cast("unsigned char", cmd), 
                                  SMBUS.I2C_SMBUS_I2C_BLOCK_BROKEN,
                                  data):
            raise IOError(ffi.errno)
       
    @property
    def pec(self):
        return self._pec

    @pec.setter
    def pec(self, value):
        if value is None:
          raise TypeError("Cannot delete attribute")
        # XXX make sure it is kind of boolean-ish
        value = bool(value)
        if pec != self._pec:
            if C.ioctl(self._fd, SMBUS.I2C_PEC, ffi.cast("int", pec)):
                raise IOError(ffi.errno)
            self._pec = pec
        


def smbus_data_to_list(block):
    return [block[i+1] for i in range(block[0])]

def list_to_smbus_data(data, vals):
    if len(vals) > 32 or len(vals) == 0:
        raise OverflowError("Third argument must be a list of at least one, "
                            "but not more than 32 integers")
    data.block[0] = len(vals)
    for i, val in enumerate(vals):
        data.block[i] = val
