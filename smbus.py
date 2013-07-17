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

from cffi import FFI
ffi = FFI()
ffi.cdef("""
#define O_RDWR ...
int open(const char *pathname, int flags, int mode);
""")
C = ffi.verify("""
#include <fcntl.h>
""")

MAXPATH=16

class SMBus(object):
    fd = -1
    addr = -1
    pec = 0

    def __init__(self, bus=-1):
        if bus >= 0:
            self.open(bus)

    def close(self):
        """Disconnects the object from the bus."""
        if self.fd != -1 and close(self.fd):
            raise IOError
        self.fd = -1
        self.addr = -1
        self.pec = 0

    def dealloc(self):
        self.close()

    def open(self, bus):
	"""Connects the object to the specified SMBus."""
        bus = int(bus)
        path = "/dev/i2c-%d" % (bus,)
        if len(path) >= MAXPATH:
                raise OverflowError("Bus number is invalid.")

        self.fd = C.open(path, C.O_RDWR, 0)
        if self.fd == -1:
            raise IOError(ffi.errno)

