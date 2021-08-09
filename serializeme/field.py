from serializeme.exceptions import *

"""
Field object to store a related name, size, and value of a field.
"""
# Author: Justin Roosenschoon <jeroosenschoon@gmail.com>

# Licence: MIT License (c) 2021 Justin Roosenschoon

NULL_TERMINATE       = "null_terminate"
PREFIX_LENGTH        = "prefix_length"
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"
IPV4                 = "ipv4"
HOST                 = "host"

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
        # Size == number of bits, string of bits/bytes, or string of CONST.
        if type(size) is int:
            if type(value) is int:
                # Type and size are both integer. So we have a specified number
                # with a specified number of bits.
                # First, make sure this number can fit in the bits.
                if self.__can_fit(size, value):
                    if size % 8 == 0:
                        # Bits can be represented as a certain number of bytes,
                        # so we will do just that. The size is the number of times
                        # 8 goes into the number of bits.
                        self.size = size // 8
                        # Since we have whole bytes, we can encode the
                        # value already.
                        self.value = value.to_bytes(size // 8, 'big')
                        self.value_type = "bytes"
                    else:
                        # Bits cannot evenly be represented by a certain number
                        # of bits. Just keep the size and value the same with
                        # a type of bits.
                        self.size = size
                        self.value = value
                        self.value_type = "bits"
                else:
                    if size == 1:
                        raise ValueTooBig(1, value, "bit")
                    elif size > 1:
                        raise ValueTooBig(size, value, "bits")
            elif type(value) is bytes:
                if size == len(value):
                    # The size of the value is exactly the size specified.
                    # We can put the size and value directly in.
                    self.size = size
                    self.value = value
                    self.value_type = "bytes"
                elif size > len(value):
                    # The specified size is more than the size of the value.
                    # We will add a padding of 0 to make them the same.
                    self.size = size # The size is the same.
                    # The padding + the value
                    self.value = b'\x00' * (size - (len(value))) + value
                    self.value_type = "bytes" # Type is still bytes.
                else:
                    # Value cannot fit in specified size. Raise an error.
                    if size == 1:
                        # Size is only 1 so singular byte in error message.
                        raise ValueTooBig(size, value, "byte")
                    else:
                        # Size is > 1 so plural byte in error message.
                        raise ValueTooBig(size, value, "bytes")
            else:
                # Currently, when size is an integer, we can give integer
                # or byte values. If those are not used, throw an error.
                raise InvalidValue(value)
        elif type(size) is str:
            # Currently when size is str, it must be one of the specified values.
            if size == IPV4:
                # Lots of stuff to check, so call private helper function to handle.
                self.__handle_ipv4(value)
            elif size == HOST:
                # This will just encode the value and make the size the number
                # of bytes of that encoding.
                self.value   = value.encode()
                self.size    = len(self.value)
                self.value_type = HOST
            elif size == PREFIX_LENGTH:
                # Lots of stuff to check, so call private helper function to handle.
                self.__handle_prefix_len(value)
            elif size == PREFIX_LEN_NULL_TERM:
                # If the value is 0, change it to undefined. This will serve as
                # a placeholder so we can set it later. This must be set before
                # packetize is called.
                if value == 0:
                    self.size = -1
                    self.value = "undefined"
                    self.value_type = PREFIX_LEN_NULL_TERM
                else:
                    # We have a value to handle. Call a helper since
                    # there is a lot.
                    self.__handle_prefix_len(value)
                    self.size += 1 # We add 1 to size for null byte.
                    self.value +=  b'\x00' # Add the null byte.
                    self.value_type = PREFIX_LEN_NULL_TERM
            elif size == NULL_TERMINATE:
                # If the value is 0, change it to undefined. This will serve as
                # a placeholder so we can set it later. This must be set before
                # packetize is called.
                if value == 0:
                    self.size = -1
                    self.value = "undefined"
                    self.value_type = NULL_TERMINATE
                else:
                    # All we have to do is encode the value and add a byte of
                    # zeros.
                    # Also add 1 to the size for this additional byte of zeros.
                    self.size = len(value.encode()) + 1
                    self.value = value.encode() + b'\x00'
                    self.value_type = NULL_TERMINATE
            else:
                # The string is not one we know, so raise an error.
                raise InvalidSize(size, msg="Invalid string for size")
        else:
            # Currently size can only be an integer or a string. If it is
            # neither, raise an error
            raise InvalidSize(type(size))
        # The name will always be the same.
        self.name = name

    def to_binary(self):
        """
        Convert field to binary string of length self.size with value self.value.
        :return: Binary string of field.
        """
        if type(self.value) is int:
            # Integer value. Just convert to binary with bin() and remove the 0b
            # part at the start.
            return bin(self.value).lstrip("0b")
        elif type(self.value) is bytes:
            # Our value is bytes we need to loop through each one, and convert
            # them to binary and remove the 0b at the start.
            m = ''
            for b in self.value:
                a = bin(b).lstrip("0b")
                # If the binary number of the current byte is not 8 bits, add
                # all a padding of 0s at the start to make it 8 bits, and then
                # add an _ to seperate each group of 8 bits.
                # We will have an extra _ at the end, so we will remove it later.
                m += '0'*(8-len(a)) + a + "_"
            return m[:-1] # Remove the last _ of the bit string.
        elif type(self.value) is str:
            # The value is either "undefined" or a special constant.
            # If undefined, just return undefined.
            if self.value == "undefined":
                return "undefined"
            else:
                # Do the same thing as bytes. Loop through the bytes, and convert
                # them to binary and remove the 0b at the start.
                m = ''
                for b in self.value.encode():
                    a = bin(b).lstrip("0b")
                    # If the binary number of the current byte is not 8 bits, add
                    # all a padding of 0s at the start to make it 8 bits, and then
                    # add an _ to seperate each group of 8 bits.
                    # We will have an extra _ at the end, so we will remove it later.
                    m += '0'*(8-len(a)) + a + "_"
                return m[:-1] # Remove the last _ of the bit string.

    def to_hex(self):
        """
        Convert field to hex string of length self.size/4 with value self.value.
        :return: Hex string of field.
        """
        if type(self.value) is int:
            # We have an integer value. Just return hex version of it.
            return hex(self.value)
        elif type(self.value) is bytes:
            # We already have a bytes object. This is already represented as
            # a hex number. We can just return the value directly.
            return self.value
        elif type(self.value) is str:
            # If we have a string, and it is "undefined", return undefined.
            # Otherwise, return the encoded string.
            if self.value == "undefined":
                return "undefined"
            else:
                return self.value.encode()

    def __str__(self):
        """
        String representation of field of the form:
        Field(name: [NAME], [SIZE], Value: [VALUE])
        :return: String representation of field
        """
        return 'Field(name: {}, size: {}, value: {})'.format(self.name, self.size, self.value)

    def __can_fit(self, size, value):
        """
        Make sure the specificed value can fit in the specified number of bits.

        :param size: The number of bits to check.
        :param value: The value to see if it can fit in the number of bits.
        """
        return value.bit_length() <= size

    def __handle_ipv4(self, value):
        """
        Handle an IPv4 address. Make sure it is a valid address, and if so,
        store it in self.value. Also make self.size = 32 since IPv4 addresses
        are 32-bits (4 bytes).

        :param value: The value to determine if it is a valid IPv4 address, and
                      if so, set self.value to it.
        """
        if value == 0:
            # If the value is 0, this field will be a placeholder waiting to be
            # filled in the future. It must be filled before packetize() is called.
            self.size = -1
            self.value = "undefined"
        elif type(value) is str:
            # The value is string, so it must be of form "X.X.X.X"
            # We will split it and make sure there are four elements in the
            # Resulting array. Otherwise, through an error.
            if len(value.split(".")) != 4:
                raise InvalidIPv4Address(value, "IPv4 Addresses must have 4 numbers.")
            self.size = 32 #IPv4 have 32 bits.
            # We will loop through each number in the list and make sure that
            # number is between 0 and 255 for a valid IPv4 address.
            self.value = b''
            for v in value.split("."):
                v_int = int(v)
                if v_int < 0 or v_int > 255:
                    # IPv4 address is not valid with a negative number or one
                    # greater than 255.
                    raise InvalidIPv4Address(value, "IPv4 numbers must be between 0-255.")
                else:
                    # Valid number. Add the byte-encoded number to the value.
                    self.value += v_int.to_bytes(1, 'big')
        elif type(value) is tuple:
            # The tuple must have exactly 4 numbers. If not, throw an error.
            if len(value) != 4:
                raise InvalidIPv4Address(value, "IPv4 Addresses must have 4 numbers.")
            self.size = 32 #IPv4 have 32 bits.
            # Loop through each value, make sure it is a valid number, and if so,
            # add it to the value.
            self.value = b''
            for v in value:
                if v < 0 or v > 255:
                    # IPv4 address is not valid with a negative number or one
                    # greater than 255.
                    raise InvalidIPv4Address(value, "IPv4 numbers must be between 0-255.")
                else:
                    # Valid number. Add the byte-encoded number to the value.
                    self.value += v.to_bytes(1, 'big')
        else:
            # We currently only support strings or tuples for an IPv4 value. If
            # it is not one of these, we will throw an error.
            raise InvalidIPv4Address(value)
        self.value_type = IPV4 # Type is always IPv4

    def __handle_prefix_len(self, value):
        """
        Handle a value that needs its length prefixed to it or each element in it.

        :param value: The value, or values to add the length(s) to.
        """
        if type(value) is str:
            # If the value is a string, we will encode it and add the length of
            # it to the front.
            len_bytes = len(value.encode()) # Length of value.
            # The length of the value (as a byte) + the actual (encoded) value.
            self.value = len_bytes.to_bytes(1, "big") + value.encode()
            # Size is the length of the value + 1 to account for the prefixed
            # length.
            self.size = 1 + len_bytes
        elif type(value) is tuple:
            # If the value is a tuple, we will loop through each value, and add
            # its length and encoded value to self.value.
            self.value = b''
            for v in value:
                len_bytes = len(v.encode()) # Length of value.
                # Add the byte representing the length + the encoded value.
                self.value += len_bytes.to_bytes(1, "big") + v.encode()
            # We can just set the size of our field to the be size of the
            # generated value which has the length and the values already.
            self.size = len(self.value)
        else:
            # Currently only support a string or tuple value. If it is something
            # else, throw an error.
            raise InvalidValue(type(value))
        self.value_type = PREFIX_LENGTH
