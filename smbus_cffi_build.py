from cffi import FFI
import os

module_name = '_smbus_cffi'

ffi = FFI()

ffi.cdef("""
typedef unsigned char __u8;
typedef int32_t __s32;
typedef unsigned short int __u16;

#define I2C_SLAVE ...
#define I2C_PEC ...

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
#define I2C_SMBUS_BLOCK_MAX         ...    /* As specified in SMBus standard */
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

include_dir = os.path.join(os.path.dirname(__file__), 'include')

ffi.set_source(module_name, """
#include <sys/types.h>
#include <linux/i2c-dev.h>
""", include_dirs=[include_dir])

if __name__ == '__main__':
    ffi.compile()
