from serializeme.exceptions import *

"""
Field object to store a related name, size, and value of a field.
"""
# Author: Justin Roosenschoon <jeroosenschoon@gmail.com>

# Licence: MIT License (c) 2021 Justin Roosenschoon

NULL_TERMINATE = "null_terminate"
PREFIX_LENGTH  = "prefix_length"
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"
IPV4 = "ipv4"
HOST = "host"

VAR_PREFIXES = [NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM, IPV4, HOST]


class Field:
    """
    Field object to store a related name, size, and value of a field.

    Parameters
    ----------
    :param name: The name of the field.
    :param size: The number of bits of the field.
    :param value: (default=0) The value of the field.
    """
    def __init__(self, name, size=1, value=0):
        # Size == num bits or CONST.
        if type(size) is int:
            if type(value) is int:
                if self.can_fit_(size, value):
                    if size % 8 == 0:
                        self.size = size//8
                        self.value = value.to_bytes(size//8, 'big')
                        self.special = "bytes"
                    else:
                        self.size = size
                        self.value = value
                        self.special = "bits"
                else:
                    if size == 1:
                        raise ValueTooBig(1, value, "bit")
                    elif size > 1:
                        raise ValueTooBig(size, value, "bits")
            elif type(value) is bytes:
                if size == len(value):
                    self.size = size
                    self.value = value
                    self.special = "bytes"
                elif size > len(value):
                    self.size = size 
                    self.value = value + b'\x00' * (size-(len(value)))
                    self.special = "bytes"
                else:
                    if size == 1:
                        raise ValueTooBig(size, value, "byte")
                    else:
                        raise ValueTooBig(size, value, "bytes")
            else:
                raise InvalidValue(value)
        elif type(size) is str:
            # SPECIAL SIZE.
            if size == IPV4: 
                self.handle_ipv4_(value)
            elif size == HOST:
                self.value   = value.encode()
                self.size    = len(self.value)
                self.special = HOST
            elif size == PREFIX_LENGTH:
                self.handle_prefix_len_(value)
            elif size == PREFIX_LEN_NULL_TERM:
                if value == 0:
                    self.size = -1
                    self.special = PREFIX_LEN_NULL_TERM
                    self.value = "undefined" 
                else:
                    self.handle_prefix_len_(value)
                    self.size += 1 # for null byte
                    self.special = PREFIX_LEN_NULL_TERM
                    self.value +=  b'\x00'

            elif size == NULL_TERMINATE:
                if value == 0: 
                    self.size = -1
                    self.special = NULL_TERMINATE
                    self.value = "undefined" 
                else:
                    self.size = len(value.encode()) + 1
                    self.value = value.encode() + b'\x00'
                    self.special = NULL_TERMINATE
            else:
                raise InvalidSize(size, msg="Invalid string for size")
        else:
            raise InvalidSize(type(size))
        self.name = name

    def to_binary(self):
        """
        Convert field to binary string of length self.size with value self.value.
        :return: Binary string of field.
        """
        if type(self.value) is int:
            return bin(self.value)[2:]
        elif type(self.value) is bytes:
            m = ''
            for b in self.value:
                a = bin(b).lstrip("0b")
                m += '0'*(8-len(a)) + a + "_"
            return m[:-1]
        elif type(self.value) is str:
            if self.value == "undefined":
                return "undefined"
            else:
                m = ''
                for b in self.value.encode():
                    a = bin(b).lstrip("0b")
                    m += '0'*(8-len(a)) + a + "_"
                return m[:-1]

    def to_hex(self):
        """
        Convert field to hex string of length self.size/4 with value self.value.
        :return: Hex string of field.
        """
        if type(self.value) is int:
            return hex(self.value)
        elif type(self.value) is bytes:
            return self.value
        elif type(self.value) is str:
            if self.value == "undefined":
                return "undefined"
            else:
                return self.value.encode()

    def __str__(self):
        """
        String representation of field of form Field [name: [NAME], [SIZE], Value: [VALUE]]
        :return: String representation of field
        """
        return 'Field(name: {}, size: {}, value: {})'.format(self.name, self.size, self.value)

    def can_fit_(self, size, value):
        return value.bit_length() <= size

    def handle_ipv4_(self, value):
        if value == 0: 
            self.size = -1
            self.value = "undefined" 
        elif type(value) is str:
            if len(value.split(".")) != 4:
                raise InvalidIPv4Address(value, "IPv4 Addresses must have 4 numbers.")
            self.size = 32 #IPv4 have 32 bits.
            self.value = b''
            for v in value.split("."):
                v_int = int(v)
                if v_int < 0 or v_int > 255:
                    raise InvalidIPv4Address(value, "IPv4 numbers must be between 0-255.")
                else:
                    self.value += v_int.to_bytes(1, 'big')
        elif type(value) is tuple:
            if len(value) != 4:
                raise InvalidIPv4Address(value, "IPv4 Addresses must have 4 numbers.")
            self.size = 32 #IPv4 have 32 bits.
            self.value = b''
            for v in value:
                if v < 0 or v > 255:
                    raise InvalidIPv4Address(value, "IPv4 numbers must be between 0-255.")
                else:
                    self.value += v.to_bytes(1, 'big')
        else:
            raise InvalidIPv4Address(value)
        self.special = IPV4

    def handle_prefix_len_(self, value):
        if type(value) is str:
            len_bytes = len(value.encode())
            self.value = len_bytes.to_bytes(1, "big") + value.encode()
            self.size = 1 + len_bytes
        elif type(value) is tuple:
            self.value = b''
            for v in value:
                len_bytes = len(v.encode())
                self.value += len_bytes.to_bytes(1, "big") + v.encode()
            
            self.size = len(self.value) 
        else:
            raise InvalidValue(type(value))
        self.special = PREFIX_LENGTH