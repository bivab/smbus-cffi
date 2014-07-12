import pytest
from smbus import ffi, list_to_smbus_data, smbus_data_to_list


def test_list_to_smbus_data():
    lst = range(10)
    data = ffi.new("union i2c_smbus_data *")
    list_to_smbus_data(data, lst)
    assert data.block[0] == 10
    for i in lst:
        assert data.block[i + 1] == i


def test_smbus_data_to_list():
    lst = range(10)
    data = ffi.new("union i2c_smbus_data *")
    list_to_smbus_data(data, lst)
    assert smbus_data_to_list(data) == range(10)


def test_list_to_smbus_data_errors():
    data = ffi.new("union i2c_smbus_data *")
    l = range(33)
    with pytest.raises(OverflowError):
        list_to_smbus_data(data, l)
    # does not raise
    list_to_smbus_data(data, range(32))


def test_list_to_smbus_full():
    lst = range(1, 33)
    data = ffi.new("union i2c_smbus_data *")
    list_to_smbus_data(data, lst)
    assert data.block[0] == len(lst)
    for i in range(len(lst)):
        assert data.block[i + 1] == i + 1
