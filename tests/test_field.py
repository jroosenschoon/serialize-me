"""
Test cases for Field.py.

Author: Justin Roosenschoon
License: MIT License (c) 2021 Justin Roosenschoon
"""
import pytest
import serializeme
from serializeme.field import Field
from serializeme import IPV4, HOST, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM, NULL_TERMINATE


# ============================ Bit field ==============================
def test_valid_bit_fields():
    """Test the ability for Field.py to handle valid bit entries."""
    f1 = Field("OneBit0Val", size=1, value=0)
    f2 = Field("OneBit1Val", size=1, value=1)
    f3 = Field("SixBit0Val", size=6, value=0)
    f4 = Field("SixBit63Val", size=6, value=63)  # Max value for 6 bits

    assert str(f1) == "Field(name: OneBit0Val, size: 1, value: 0)"
    assert f1.value_type == "bits"
    assert str(f2) == "Field(name: OneBit1Val, size: 1, value: 1)"
    assert f2.value_type == "bits"
    assert str(f3) == "Field(name: SixBit0Val, size: 6, value: 0)"
    assert f3.value_type == "bits"
    assert str(f4) == "Field(name: SixBit63Val, size: 6, value: 63)"
    assert f4.value_type == "bits"


def test_invalid_bit_fields():
    """Test the ability for Field.py to handle an invalid bit entry."""
    with pytest.raises(serializeme.exceptions.ValueTooBig):
        # Max size should be 3
        f1 = Field("invalidField", size=2, value=5)


# ============================ Byte field ==============================
def test_valid_byte_field_with_exact_size():
    """Handle a byte entry with the size the exact number  of the value's bytes."""
    f1 = Field("validField", size=3, value=b'abc')

    assert str(f1) == "Field(name: validField, size: 3, value: abc)"
    assert f1.value_type == "bytes"


def test_valid_byte_field_with_bigger_size():
    """Handle a byte entry with the size the bigger than number of the value's bytes."""
    f1 = Field("validField", size=10, value=b'abc1def2')

    assert f1.value == b'abc1def2\x00\x00'
    assert f1.value_type == "bytes"


def test_invalid_byte_field_with_smaller_size():
    """Handle a byte entry with the size the smaller than number of the value's bytes."""
    with pytest.raises(serializeme.exceptions.ValueTooBig):
        f1 = Field("invalidField", size=3, value=b'abc1def2')


# ============================ IPv4 field ==============================
def test_valid_ipv4_str():
    """Handle a valid string IPv4 address entry. """
    f = Field("validIPv4", size=IPV4, value="10.3.102.2")
    assert f.value == bytearray([10, 3, 102, 2])
    assert f.value_type == IPV4
    assert f.size == 32


def test_valid_ipv4_tuple():
    """Handle a valid tuple IPv4 address entry. """
    f = Field("validIPv4", size=IPV4, value=(10, 3, 102, 2))
    assert f.value == bytearray([10, 3, 102, 2])
    assert f.value_type == IPV4
    assert f.size == 32


def test_valid_ipv4_undefined():
    """Handle a valid IPv4 address meant to be filled in later. """
    f = Field("toBeDefinedLater", size=IPV4, value=0)
    assert f.value == "undefined"
    assert f.value_type == IPV4
    assert f.size == -1


def test_invalid_ipv4_number_too_big_with_str_entry():
    """Handle an invalid string IPv4 address that has a number greater than 255."""
    with pytest.raises(serializeme.exceptions.InvalidIPv4Address):
        f = Field("invalidField", size=IPV4, value="10.1.256.1")


def test_invalid_ipv4_number_too_big_with_tuple_entry():
    """Handle an invalid tuple IPv4 address that has a number greater than 255."""
    with pytest.raises(serializeme.exceptions.InvalidIPv4Address):
        f = Field("invalidField", size=IPV4, value=(10, 1, 256, 1))


def test_invalid_ipv4_number_too_small_with_str_entry():
    """Handle an invalid string IPv4 address that has a number less than 0."""
    with pytest.raises(serializeme.exceptions.InvalidIPv4Address):
        f = Field("invalidField", size=IPV4, value="10.1.-1.1")


def test_invalid_ipv4_number_too_small_with_tuple_entry():
    """Handle an invalid tuple IPv4 address that has a number less than 0."""
    with pytest.raises(serializeme.exceptions.InvalidIPv4Address):
        f = Field("invalidField", size=IPV4, value=(10, 1, -2, 1))


# ============================ Host field ==============================
def test_host_field():
    """Handle a host entry. """
    f = Field("validHost", size=HOST, value="serializeme")
    assert f.value == "serializeme".encode()
    assert f.value_type == HOST
    assert f.size == len("serializeme")


def test_valid_host_undefined():
    """Handle a valid host meant to be filled in later. """
    f = Field("toBeDefinedLater", size=HOST, value=0)
    assert f.value == "undefined"
    assert f.value_type == HOST
    assert f.size == -1


# ============================ Prefix length field ==============================
def test_prefix_length_string_field():
    """Handle a prefix length string entry. """
    f = Field("validPrefixLength", size=PREFIX_LENGTH, value="serializeme")
    l = len("serializeme")
    assert f.value == l.to_bytes(1, 'big') + "serializeme".encode()
    assert f.value_type == PREFIX_LENGTH
    assert f.size == len("serializeme") + 1


def test_prefix_length_tuple_field():
    """Handle a prefix length tuple entry. """
    f = Field("validPrefixLength", size=PREFIX_LENGTH, value=("serializeme", "networking", "is", "cool"))
    l = len("serializemenetworkingiscool")
    msg = b''
    for v in ("serializeme", "networking", "is", "cool"):
        msg += len(v.encode()).to_bytes(1, "big") + v.encode()

    assert f.value == msg
    assert f.value_type == PREFIX_LENGTH
    assert f.size == l + 4


def test_valid_prefix_length_undefined():
    """Handle a valid Prefix length address meant to be filled in later. """
    f = Field("toBeDefinedLater", size=PREFIX_LENGTH, value=0)
    assert f.value == "undefined"
    assert f.value_type == PREFIX_LENGTH
    assert f.size == -1


# ============================ Prefix length null terminate field ==============================
def test_prefix_length_null_terminate_string_field():
    """Handle a prefix length null termination string entry. """
    f = Field("validPrefixLengthNullTerminate", size=PREFIX_LEN_NULL_TERM, value="serializeme")
    l = len("serializeme")
    assert f.value == l.to_bytes(1, 'big') + "serializeme".encode() + b'\x00'
    assert f.value_type == PREFIX_LEN_NULL_TERM
    assert f.size == l + 2


def test_prefix_length_null_terminate_tuple_field():
    """Handle a prefix length null termination tuple entry. """
    f = Field("validPrefixLengthNullTerminate", size=PREFIX_LEN_NULL_TERM, value=("serializeme", "networking", "is", "cool"))
    l = len("serializemenetworkingiscool")
    msg = b''
    for v in ("serializeme", "networking", "is", "cool"):
        msg += len(v.encode()).to_bytes(1, "big") + v.encode()

    assert f.value == msg + b'\x00'
    assert f.value_type == PREFIX_LEN_NULL_TERM
    assert f.size == l + 5


def test_valid_prefix_length_null_terminate_undefined():
    """Handle a valid Prefix length null terminate field meant to be filled in later. """
    f = Field("toBeDefinedLater", size=PREFIX_LEN_NULL_TERM, value=0)
    assert f.value == "undefined"
    assert f.value_type == PREFIX_LEN_NULL_TERM
    assert f.size == -1


# ============================ Null terminate field ==============================
def test_null_terminate_string_field():
    """Handle a prefix length null termination string entry. """
    f = Field("validNullTerminate", size=NULL_TERMINATE, value="serializeme")
    l = len("serializeme")
    assert f.value == "serializeme".encode() + b'\x00'
    assert f.value_type == NULL_TERMINATE
    assert f.size == l + 1


def test_valid_null_terminate_undefined():
    """Handle a valid Prefix length null terminate field meant to be filled in later. """
    f = Field("toBeDefinedLater", size=NULL_TERMINATE, value=0)
    assert f.value == "undefined"
    assert f.value_type == NULL_TERMINATE
    assert f.size == -1


# ============================ Binary string testing ============================
def test_bit_exact_size_binary_string():
    f = Field("testField", size=9, value=345)
    assert f.to_binary() == "101011001"


def test_bit_greater_size_binary_string():
    f = Field("testField", size=14, value=345)
    assert f.to_binary() == "10101100100000"


def test_byte_exact_size_binary_string():
    f = Field("testField", size=5, value=b'e\x00:\x05b')
    assert f.to_binary() == "01100101_00000000_00111010_00000101_01100010"


def test_byte_greater_size_binary_string():
    f = Field("testField", size=7, value=b'e\x00:\x05b')
    assert f.to_binary() == "01100101_00000000_00111010_00000101_01100010_00000000_00000000"


def test_special_undefined_binary_string():
    f = Field("testField", size=IPV4, value=0)
    assert f.to_binary() == "undefined"


def test_ipv4_binary_string():
    f = Field("testField", size=IPV4, value="10.3.102.2")
    assert f.to_binary() == "00001010_00000011_01100110_00000010"


def test_host_binary_string():
    f = Field("testField", size=HOST, value="abc.d")
    assert f.to_binary() == "01100001_01100010_01100011_00101110_01100100"


def test_prefix_length_with_str_binary_string():
    f = Field("testField", size=PREFIX_LENGTH, value="abc.d")
    assert f.to_binary() == "00000101_01100001_01100010_01100011_00101110_01100100"


def test_prefix_length_tuple_binary_string():
    f = Field("testField", size=PREFIX_LENGTH, value=("test", "com", "ex"))
    assert f.to_binary() == "00000100_01110100_01100101_01110011_01110100_00000011_01100011_01101111_01101101_00000010_01100101_01111000"


def test_null_term_binary_string():
    f = Field("testField", size=NULL_TERMINATE, value="abc.d")
    assert f.to_binary() == "01100001_01100010_01100011_00101110_01100100_00000000"


def test_prefix_length_null_term_binary_string():
    f = Field("testField", size=PREFIX_LEN_NULL_TERM, value="abc.d")
    assert f.to_binary() == "00000101_01100001_01100010_01100011_00101110_01100100_00000000"


# ============================ Hex string testing ============================
def test_bit_exact_size_hex_string():
    f = Field("testField", size=9, value=345)
    assert f.to_hex() == "0x159"


def test_bit_greater_size_hex_string():
    f = Field("testField", size=14, value=345)
    assert f.to_hex() == "0x159"


def test_byte_exact_size_hex_string():
    f = Field("testField", size=5, value=b'e\x00:\x05b')
    assert f.to_hex() == b'e\x00:\x05b'


def test_byte_greater_size_hex_string():
    f = Field("testField", size=7, value=b'e\x00:\x05b')
    assert f.to_hex() == b'e\x00:\x05b\x00\x00'


def test_special_undefined_hex_string():
    f = Field("testField", size=IPV4, value=0)
    assert f.to_hex() == "undefined"


def test_ipv4_hex_string():
    f = Field("testField", size=IPV4, value="10.3.102.2")
    assert f.to_hex() == b'\n\x03\x66\x02'


def test_host_hex_string():
    f = Field("testField", size=HOST, value="abc.d")
    assert f.to_hex() == b'abc.d'


def test_prefix_length_with_str_hex_string():
    f = Field("testField", size=PREFIX_LENGTH, value="abc.d")
    assert f.to_hex() == b'\05abc.d'


def test_prefix_length_tuple_hex_string():
    f = Field("testField", size=PREFIX_LENGTH, value=("test", "com", "ex"))
    assert f.to_hex() == b'\04test\03com\02ex'


def test_null_term_hex_string():
    f = Field("testField", size=NULL_TERMINATE, value="abc.d")
    assert f.to_hex() == b"abc.d\x00"


def test_prefix_length_null_term_hex_string():
    f = Field("testField", size=PREFIX_LEN_NULL_TERM, value="abc.d")
    assert f.to_hex() == b'\05abc.d\00'
