"""
Serialize object that can encode data into a byte array.
"""
# Author: Justin Roosenschoon <jeroosenschoon@gmail.com>

# Licence: MIT License (c) 2021 Justin Roosenschoon

import re
from math import ceil
from socket import inet_aton
from serializeme.field import Field
from serializeme.exceptions import *
from collections import MutableMapping

# Constants representing various ways to handle variable-length data.
NULL_TERMINATE = "null_terminate"  # Data + byte of zeros
PREFIX_LENGTH = "prefix_length"  # Length of data (in bytes) + Data
# Length of data (in bytes) + Data + bytes of zeros
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"
IPV4 = "ipv4"
HOST = "host"
VAR_PREFIXES = [NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM, IPV4, HOST]


class Serialize(MutableMapping):
    """
    Serialize object that can encode data into a byte array. This allows users to
    enter values and the desired size (in bits or bytes), and the Serialize object
    will automatically handle the conversion of these values to a byte array.
    Serialize also supports specially formatted data by one of the above constants.
    Parameters
    ----------
    :param data: dictionary
        The data to be converted to a byte array. The dictionary key-value pairs
        are of the form field_name: name: <field-info> where <field-info> is one of:
            - A single integer specifying the number of bits the field is with
              a value of 0.
            - A string of the form "xb" where x is the number of bits.
            - A string of the form "xB" where x is the number of bytes.
            - A two-tuple of form (a, b) with a, b being integers. a is the number
              of bits, and b is the value to store in the field.
            - A two-tuple of form (a, b) with a being a string and b being a number.
              a (the string) is of the form "xb" where x is the number of bits or
              "xB" where x is the number of bytes. b is an integer representing
              the value of the field.
            - A two-tuple of the form (a, b) with a being a constant string defined
              from above and b is the format correlated to that constant.
        If any of the values cannot be held in the specified number of bits or
        bytes, an exception will be thrown.

    Attributes
    ----------
    fields: list of Field objects representing the Fields that were generated
            by the dictionary.
    """
    def __init__(self, data):
        self.fields = self.__extract_fields(data)

    def packetize(self):
        """
        Generate a byte string from the list of fields in the object.
        :return: A byte string of the fields.
        """
        t_byte = ''   # Temporary bit string to add up to build bytes from bits.
        b = b''       # Final byte string to be built.
        for field in self.fields:
            # If any field has a size of -1, it must not have been initialized.
            # We cannot build a byte string as a result. Therefore, throw an error.
            if field.size == -1:
                raise UninitializedField(field.name)
            else:
                # If we have bits, we must have a series of consecutive bit
                # fields that can create bytes. If not, throw an error.
                if field.special == "bits":
                    if len(t_byte) + field.size == 8:
                        # We have 8 bits. Convert it to a byte and add it to byte
                        # string. Also reset the temp byte string.
                        b += self.__bits_to_byte(t_byte + bin(field.value)[2:])
                        t_byte = '' # Restart the temp byte.
                    elif len(t_byte) + field.size < 8:
                        # We have not yet reached 8 bits. Add the next series of
                        # bytes onto it.
                        a = bin(field.value)[2:]
                        t_byte += "0" * (field.size - len(a)) + a
                    else:
                        # We have more than 8 bits. This cannot form a byte, so
                        # throw an error.
                        raise InvalidBitNumber()
                else:
                    # We have bytes. we can add these directly.
                    if len(t_byte) == 0:
                        # If there is no temp_byte to add, just add the field
                        # directly.
                        b += field.value
                    elif len(t_byte) == 8:
                        # If we have a temp_byte to add, add this, and the field.
                        # Then reset the temp byte.
                        b += t_byte + field.value
                        t_byte = ''
                    else:
                        # We do not have the correct number of bits. Throw an
                        # error.
                        raise InvalidBitNumber()

        return b

    def get_field(self, field_name):
        """
        Get a specified field from the fields list, or raise an error if specified
        field does not exist. If field does not exist, raise FieldNotFound
        exception.
        :param field_name: The name of the desired field to find.
        :return: Field: Field object with the specified name.
        """
        # If field exists, call __getitem__. Otherwise, raise an error.
        if self.field_exists(field_name):
            self.__getitem__(field_name)
        raise FieldNotFound(field_name)

    def set_field(self, field_name, value):
        """
        Set a field from the fields list, or return Error if specified
        field does not exist. If field does not exist, raise FieldNotFound
        exception.
        :param field_name: The name of the desired field to set.
        :param value: The value to set the field to.
        :return: Field: Field object with the specified name.
        """
        # If field exists, call __setitem__. Otherwise, raise an error.
        if self.field_exists(field_name):
            self.__setitem__(field_name, value)
        else:
            raise FieldNotFound(field_name)

    def field_exists(self, field_name):
        """
        Determine if a field exists in the self.fields dictionary.
        :param field_name The name of the field to determine its existence.
        :return True if field exists. False otherwise.
        """
        for f in self.fields:
            if f.name == field_name:
                return True
        return False

    def __delitem__(self, field_name):
        """
        Delete a specified field if it exists. If field does not exist, raise
        FieldNotFound exception.
        :param field_name: The name of the desired field to remove.
        """
        # If field exists, delete it. Otherwise, raise an error.
        if self.field_exists(field_name):
            del self.fields[field_name]
        else:
            raise FieldNotFound(field_name)

    def __getitem__(self, field_name):
        """
        Get a specified field if it exists. If field does not exist, raise
        FieldNotFound exception.
        :param field_name: The name of the desired field to get.
        :return The field associated with the specfied name (if it exists).
        """
        # If field exists, return it. Otherwise, raise an error.
        if self.field_exists(field_name):
            return self.fields[field_name]
        raise FieldNotFound(field_name)

    def __iter__(self):
        """
        Use a generator function to return the different fields.
        :return The next field.
        """
        yield from self.fields

    def __len__(self):
        """
        Get the length of the fields dictionary.
        :return The length of the field.
        """
        return len(self.fields)

    def __setitem__(self, field_name, value):
        """
        Set the value of the specifield field if it exists. If field does not exist,
        raise a FieldNotFound exception.
        :param field_name The name of the field to set.
        :param value The value to set the field to, if the field exists.
        """
        if self.field_exists(field_name):
            for field in self.fields:
                if field.name == field_name:
                    # This is the field we want to set. Figure out if this fields
                    # size supports this value. If it does not, we will raise an
                    # exception.
                    if field.special == "bytes":
                        if type(value) is int:
                            # Byte field we want to add integer value. Make sure
                            # the integer can fit in the field's size. If not,
                            # raise ValueTooBig exception.
                            if self.__can_fit(field.size*8, value):
                                field.value = value
                            else:
                                raise ValueTooBig(field.size, value)
                        elif type(value) is bytes:
                            if field.size == len(value):
                                # If the size of the specified bytes is
                                # exactly the field's size, just add it.
                                field.value = value
                            elif field.size > len(value):
                                # If the size of the specified bytes is
                                # less than the field's size, add the value and
                                # padding at the end.
                                field.value = value + b'\x00' * (field.size-(len(value)))
                            else:
                                # Value is too big to fit in field's size. Raise
                                # ValueTooBig exception.
                                raise ValueTooBig(field.size, value, "bytes")
                        else:
                            # Invalid type of value for a bytes field. Raise
                            # an InvalidValue exception.
                            raise InvalidValue(value)
                    elif field.special == "bits":
                        if type(value) is int:
                            # We have a field of bits, and the type is interger,
                            # Make sure the value's bit string size can fit. If not,
                            # raise ValueTooBig error.
                            if value.bit_length() <= field.size:
                                field.value = value
                            else:
                                raise ValueTooBig(field.size, value, "bits")
                        elif type(value) is bytes:
                            # We have a bits field, and byte value. Make sure the
                            # value can fit. If the value can fit exactly, set the field's
                            # value exactly. If the value's size is less than the
                            # field's size, add padding at the end.
                            # If the value's size is more than the field's size,
                            # raise a ValueTooBig exception.
                            if field.size == len(value)*8:
                                field.value = value
                            elif field.size > len(value)*8:
                                field.value = value + b'\x00' * (field.size-(len(value)*8))
                            else:
                                raise ValueTooBig(field.size, value, "bytes")
                        else:
                            # The type of value is not supports for a bits field.
                            # Throw an InvalidValue exception.
                            raise InvalidValue(value)
                    elif field.special == HOST:
                        if type(field.size) is int and field.size == -1:
                            # HOST field that is undefined and being set.
                            # We need to set size and value of field.
                            if type(value) is bytes:
                                # If value is bytes, just assign the value to it.
                                # and then set the size to the length of this byte
                                # string.
                                field.size = len(value)
                                field.value = value
                            elif type(value) is str:
                                # If value is strings, assign the encoded value
                                # to it, and set the size to this encoded string.
                                field.value = value.encode()
                                field.size = len(field.value)
                            else:
                                # Value type is not supported. Must be bytes or string.
                                # Raise an InvalidValue exception.
                                raise InvalidValue(value)
                        elif type(value) is bytes:
                            if field.size >= len(value):
                                field.value = value
                            else:
                                raise ValueTooBig(field.size, value, "bytes")
                        elif type(value) is str:
                            if field.size >= len(value):
                                field.value = value.encode()
                            else:
                                raise ValueTooBig(field.size, value, "bytes")
                        else:
                            raise InvalidValue(value)
                    elif field.special == IPV4:
                        if type(field.size) is int and field.size == -1:
                            # IPV4 field that is undefined and being set.
                            # We need to set size and value of field.
                            if type(value) in [str, bytes, tuple]:
                                # IPv4 is always 32 bits, or 4 bytes.
                                field.size = 32
                                # Call helper function to get the IP address, if
                                # this is a valid ip address. If not, raise an
                                # InvalidIPv4Address exception.
                                ip = self.__valid_ip(value)
                                if ip:
                                    field.value = ip
                                else:
                                    raise InvalidIPv4Address(value)
                            # elif type(value) is bytes:
                            #     # IPv4 is always 32 bits, or 4 bytes.
                            #     field.size = 32
                            #     # Call helper function to get the IP address, if
                            #     # this is a valid ip address. If not, raise an
                            #     # InvalidIPv4Address exception.
                            #     ip = self.__valid_ip(value)
                            #     if ip:
                            #         field.value = ip
                            #     else:
                            #         raise InvalidIPv4Address(value)
                            # elif type(value) is tuple:
                            #     # IPv4 is always 32 bits, or 4 bytes.
                            #     field.size = 32
                            #     # Call helper function to get the IP address, if
                            #     # this is a valid ip address. If not, raise an
                            #     # InvalidIPv4Address exception.
                            #     ip = self.__valid_ip(value)
                            #     if ip:
                            #         field.value = ip
                            #     else:
                            #         raise InvalidIPv4Address(value)
                            else:
                                # Invalid type for an IPV4 field. Must be string,
                                # bytes, or tuple. Raise InvalidIPv4Address address.
                                raise InvalidIPv4Address(value)
                        if type(field.size) is int and field.size == 32:
                            if type(value) in [bytes, str, tuple]:
                                # IPv4 is always 32 bits, or 4 bytes.
                                field.size = 32
                                # Call helper function to get the IP address, if
                                # this is a valid ip address. If not, raise an
                                # InvalidIPv4Address exception.
                                ip = self.__valid_ip(value)
                                if ip:
                                    field.value = ip
                                else:
                                    raise InvalidIPv4Address(value)
                            else:
                                # Value type not supported. Must be bytes, string,
                                # or tuple.
                                raise InvalidIPv4Address(value)
                        else:
                            raise InvalidSize(field.size, msg="Invalid size for IPv4. Expected 32 bits. Received")
                        #     # Make sure there are exactly four bytes. Otherwise,
                        #     # throw an InvalidIPv4Address exception.
                        #     if len(value) == 4:
                        #         # Loop through each value, make sure they are
                        #         # between 0 and 255. If not, raise InvalidIPv4Address
                        #         # exception
                        #         m = b''
                        #         for a in value:
                        #             if int.from_bytes(a, "big") >= 0 and int.from_bytes(a, "big") <= 255:
                        #                 m += a
                        #             else:
                        #                 raise InvalidIPv4Address(value)
                        #         field.value = m
                        #     else:
                        #         # Not four bytes. Throw an InvalidIPv4Address exception.
                        #         raise InvalidIPv4Address(value)
                        # elif type(value) is str:
                        #     v = value.split(".")
                        #     if len(v) == 4:
                        #         m = b''
                        #         for a in v:
                        #             if int(a) >= 0 and int(a) <= 255:
                        #                 m += int(a).to_bytes(1, "big")
                        #             else:
                        #                 raise InvalidIPv4Address(value)
                        #         field.value = m
                        #     else:
                        #         raise InvalidIPv4Address(value)
                        # elif type(value) is tuple:
                        #     if len(value) == 4:
                        #         m = b''
                        #         for a in value:
                        #             if int.from_bytes(a, "big") >= 0 and int.from_bytes(a, "big") <= 255:
                        #                 m += a
                        #             else:
                        #                 raise InvalidIPv4Address(value)
                        #         field.value = m
                        #     else:
                        #         raise InvalidIPv4Address(value)
                    elif field.special == PREFIX_LENGTH:
                        if type(field.size) is int and field.size == -1:
                            # PREFIX_LENGTH field that is undefined and being set.
                            # We need to set size and value of field.
                            if type(value) is str:
                                field.size = len(value) + 1
                                field.value = field.value == len(value).to_bytes(1, "big") + value.encode()
                            elif type(value) is bytes:
                                field.size = len(value) + 1
                                field.value == len(value).to_bytes(1, "big") + value
                            elif type(value) is tuple:
                                # If it is a tuple, we will prefix the length at the
                                # start of each element.
                                field.size = len("".join(value)) + len(value)
                                m = b''
                                for elt in value:
                                    if type(elt) is bytes:
                                        m += len(elt).to_bytes(1, "big") + elt
                                    elif type(elt) is str:
                                        m += len(elt).to_bytes(1, "big") + elt.encode()
                                field.value = m
                            else:
                                # Value must be of type str, bytes, or tuple.
                                # If not, raise InvalidValue exception.
                                raise InvalidValue(value)
                        if type(value) is bytes:
                            if len(value) + 1 == field.size:
                                # The length is being added at the start. Make sure
                                # the size has this and the length of the actual
                                # value. If so, we can set the value to this.
                                # If not, raise an InvalidSize exception.
                                field.value == len(value).to_bytes(1, "big") + value
                            else:
                                raise InvalidSize(field.size)
                        elif type(value) is str:
                            # The length is being added at the start. Make sure
                            # the size has this and the length of the actual
                            # value. If so, we can set the value to the encoded
                            # string. If not, raise an InvalidSize exception.
                            if len(value) + 1 == field.size:
                                field.value == len(value).to_bytes(1, "big") + value.encode()
                            else:
                                raise InvalidSize(field.size)
                        elif type(value) is tuple:
                            # If it is a tuple, we will prefix the length at the
                            # start of each element.
                            if len("".join(value)) + len(value) == field.size:
                                # Make sure the size can fit both the values and
                                # each of their sizes. If not, raise InvalidSize
                                # exception. If so, encode the string (if it one)
                                # or add the bytes directly.
                                m = b''
                                for elt in value:
                                    if type(elt) is bytes:
                                        m += len(elt).to_bytes(1, "big") + elt
                                    elif type(elt) is str:
                                        m += len(elt).to_bytes(1, "big") + elt.encode()
                                field.value = m
                            else:
                                raise InvalidSize(field.size)
                        else:
                            # PREFIX_LENGTH can only be bytes, str, tuple. If
                            # the value is not one of these, raise InvalidValue
                            # exception.
                            raise InvalidValue(value)
                    elif field.special == NULL_TERMINATE:
                        if type(field.size) is int and field.size == -1:
                            # NULL_TERMINATE field that is undefined and being set.
                            # We need to set size and value of field.
                            if type(value) is str:
                                # Encode string and add null byte. Set size to
                                # size of encoded string + 1 (for null byte)
                                field.size = len(value.encode()) + 1
                                field.value = value.encode() + b'\x00'
                            elif type(value) is bytes:
                                # Add null byte to bytes. Set size to
                                # size of bytes + 1 (for null byte)
                                field.size = len(value) + 1
                                field.value = value + b'\x00'
                            else:
                                # Value can only be string or bytes.
                                # Throw InvalidValue exception if value is not
                                # one of these.
                                raise InvalidValue(value)
                        elif type(value) is bytes:
                            # Now we need to make sure the size fits the value.
                            if len(value) + 1 == field.size:
                                # If the value's size + 1 is exactly the field's
                                # size, add the value and null byte at end.
                                # Otherwise, raise InvalidSize exception.
                                field.value = value + b'\x00'
                            else:
                                raise InvalidSize(field.size)
                        elif type(value) is str:
                            # If the value's size + 1 is exactly the field's
                            # size, add the value and null byte at end.
                            # Otherwise, raise InvalidSize exception.
                            if len(value) + 1 == field.size:
                                field.value = value.encode() + b'\x00'
                            else:
                                raise InvalidSize(field.size)
                        else:
                            # Value must be of type bytes or string. Otherwise,
                            # raise an InvalidValue exception.
                            raise InvalidValue(value)
                    elif field.special == PREFIX_LEN_NULL_TERM:
                        if type(field.size) is int and field.size == -1:
                            # PREFIX_LEN_NULL_TERM field that is undefined and
                            # being set. We need to set size and value of field.
                            if type(value) is str:
                                # We add 2 now because we need length at start and
                                # null byte at end.
                                # Encode the string, add the length of the string,
                                # add the string, and add the null byte.
                                self.size = len(value.encode()) + 2
                                self.value = len(value).to_bytes(1, "big") + value.encode() + b'\x00'
                            elif type(value) is bytes:
                                # We add 2 now because we need length at start and
                                # null byte at end.
                                # Add the length of the bytes,
                                # add the bytes, and add the null byte.
                                self.size = len(value) + 2
                                self.value = len(value).to_bytes(1, "big") + value + b'\x00'
                            elif type(value) is tuple:
                                # Loop through each element, add the length at
                                # the start, then the element, and then the null
                                # byte at the end of it all.
                                self.size = len("".join(value)) + len(value) + 1
                                m = b''
                                for a in value:
                                    m += len(value).to_bytes(1, "big") + value.encode()
                                field.value = m + b'\x00'
                            else:
                                # The value type must be str, bytes, or tuple. If
                                # not, raise an InvalidValue exception.
                                raise InvalidValue(value)
                        if type(value) is bytes:
                            # Now we need to make sure the size works.
                            # It must the size of the value + 2 (one for the length
                            # and one for the bytes). If not, raise an InvalidSize
                            # exception.
                            if len(value) + 2 == field.size:
                                field.value = len(value).to_bytes(1, "big") + value + b'\x00'
                            else:
                                raise InvalidSize(field.size)
                        elif type(value) is str:
                            # Now we need to make sure the size works.
                            # It must the size of the value + 2 (one for the length
                            # and one for the bytes). If not, raise an InvalidSize
                            # exception.
                            if len(value) + 2 == field.size:
                                field.value = len(value).to_bytes(1, "big") + value.encode()+ b'\x00'
                            else:
                                raise InvalidSize(field.size)
                        elif type(value) is tuple:
                            # Now we need to make sure the size works.
                            # It must the size of the value + one byte for the
                            # length of each element, and one for the null byte
                            # at the end. If not, raise an InvalidSize exception.
                            if len("".join(value)) + len(value) + 1 == field.size:
                                m = b''
                                for a in value:
                                    m += len(value).to_bytes(1, "big") + value.encode()
                                field.value = m + b'\x00'
                            else:
                                raise InvalidSize(field.size)
                        else:
                            # Value must be of type bytes, str, tuple. If not,
                            # throw an InvalidValue exception.
                            raise InvalidValue(value)
                    else:
                        # Field type is not recognized. Throw an error.
                        raise InvalidField(field.special, "Field type is not recognized. Field type recevied")
                    # We found the field. We can stop looping through them.
                    break
        else:
            # Field does not exist. Raise FieldNotFound exception.
            raise FieldNotFound(field_name)

    def __repr__(self):
        """
        Generate a string representation of the Serialize object by listing out all of the fields, their value,
        and their sizes.
        :return: A string representation of the Serialize object.
        """
        # Figure out biggest width each column must be.
        # Start longest at the size of the headers eg "Size" has 4 characters, so bare minimum
        # is 4 characters for this column.
        longest_size = 4
        longest_name = 4
        longest_value = 5
        for field in self.fields:
            if len(field.name) > longest_name:
                # New longest name.
                longest_name = len(field.name)
            elif len(str(field.size)) + 6 > longest_size:
                # New longest size.
                longest_size = len(str(field.size)) + 6 # (need to add 6 because of " bytes")
            elif len(str(field.value)) > longest_value:
                # New longest value.
                longest_value = len(str(field.value))

        # Now we know what the width of each column will be. Let's make the message.
        # Start table with header.
        msg = "{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n="Name", width1=longest_name, s="Size", width2=longest_size, v="Value", width3=longest_value)
        for field in self.fields:
            # Make the seperator of "----" between each row.
            msg += ("-"*(longest_name + longest_size + longest_value + 6)) + "\n"
            if field.special in VAR_PREFIXES or field.special == "bytes":
                # The size of the field will be in bytes, so we can add bytes at
                # the end of the size.
                if field.size == 1:
                    # One byte so add singular byte at the end of size.
                    msg += ("{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n=field.name, width1=longest_name, s=(str(field.size) +  " byte"), width2=longest_size, v=str(field.value), width3=longest_value))
                elif field.size == -1:
                    # Undefined field. We do not have to add byte or bytes to it.
                    msg += ("{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n=field.name, width1=longest_name, s=str(field.size), width2=longest_size, v=str(field.value), width3=longest_value))
                else:
                    # Multiple bytes so add plural byte at the end of size.
                    msg += ("{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n=field.name, width1=longest_name, s=(str(field.size) +  " bytes"), width2=longest_size, v=str(field.value), width3=longest_value))
            else:
                # field must be in bits. so we will add bit or bits at end.
                if field.size == 1:
                    # One bit so add singular bit at end of size.
                    msg += ("{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n=field.name, width1=longest_name, s=(str(field.size) +  " bit"), width2=longest_size, v=str(field.value), width3=longest_value))
                elif field.size == -1:
                    msg += ("{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n=field.name, width1=longest_name, s=str(field.size), width2=longest_size, v=str(field.value), width3=longest_value))
                else:
                    # Multiple bits so add plural bits at end of size.
                    msg += ("{n:^{width1}} | {s:^{width2}} | {v:^{width3}}\n".format(n=field.name, width1=longest_name, s=(str(field.size) +  " bits"), width2=longest_size, v=str(field.value), width3=longest_value))
        return msg

    def __can_fit(self, size, value):
        """
        Determine if the specified size (in bits) can fit the specified value.
        :param size The number of bits to check to see if it can fit the specified value.
        :param value The value to see if it can fit in the specified size.
        :return True if the value can fit in size. False otherwise.
        """
        mask = size >> 31
        return not (((~value & mask) + (value & ~mask))>> (size + ~0))

    def __valid_ip(self, ip):
        """
        Determine if the specified IPv4 address is valid. If so, return the encoded
        version. If not, return False.
        :param ip The IPv4 address to determine if valid.
        :return The encoded IPv4 address if it is valid. Otherwise, return False.
        """
        if type(ip) is str:
            # IP address must be of form "A.B.C.D".
            # When we split it by the ".", make sure the size is exactly 4.
            # If not, return False.
            values = ip.split(".")
            if len(values) != 4:
                return False
            # Proper size. Start building it, and make sure each value is between
            # 0 and 255. If not, return False because it is not a valid IPv4 address.
            # If it is, encode it and add it to ip_addr byte string.
            ip_addr = b''
            for value in values:
                value = int(value)
                if value < 0 or value > 255:
                    return False
                ip_addr += value.to_bytes(1, "big")
            return ip_addr
        elif type(ip) is tuple:
            # Make sure the tuple has exactly 4 elements. If not, return false.
            if len(ip) != 4:
                return False
            # Proper size. Start building it, and make sure each value is between
            # 0 and 255. If not, return False because it is not a valid IPv4 address.
            # If it is, encode it and add it to ip_addr byte string.
            ip_addr = b''
            for value in ip:
                if value < 0 or value > 255:
                    return False
                ip_addr += value.to_bytes(1, "big")
            return ip_addr
        elif type(ip) is bytes:
            # Make sure there are exactly 4 bytes. If not, return false.
            if len(ip) != 4:
                return False
            # We have the right size. Now we need to make sure each byte is the
            # correct size (between 0 and 255). If not, return False. Otherwise,
            # simply return the byte string back.
            for b in bytes:
                b = int.from_bytes(b, "big")
                if b < 0 or b > 255:
                    return False
            return ip
        # Ipv4 address must be str, tuple, or bytes. This is an unrecognized type
        # so return false.
        return False

    def __bits_to_byte(self, bits):
        """
        Convert the specified bits to bytes.
        :param bits The bits to covnert to bytes.
        :return A bytestring representing the specified bits.
        """
        return int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder='big')

    def __extract_fields(self):
        """
        Helper function to parse the user-specified dictionary of fields upon
        creation of Serialize object.
        """
        fields = []
        for name, item in data.items():
            if item == ():
                # Field with value 0 and size 1 bit
                fields.append(Field(name, 1, 0))
            elif type(item) is int:
                # Field with specified size of bits and value 0
                fields.append(Field(name, item, 0))
            elif type(item) is  str:
                # One of three: bit, byte, or in CONSTANTS
                if re.fullmatch(r"[1-9][0-9]*b", item):
                    # Specifying number of bits with value 0
                    fields.append(Field(name, int(item[:-1]), 0))
                elif re.fullmatch(r"[1-9][0-9]*B", item):
                    # Specifying number of bytes with value 0
                    fields.append(Field(name, int(item[:-1])*8, 0))
                elif item.lower() in CONSTANTS:
                    # Field is a special type, but still has value 0
                    fields.append(Field(name, item.lower(), 0))
                else:
                    # Unknown string type. Throw error.
                    raise InvalidSize(item, msg="Invalid string for size")
            elif type(item) is tuple:
                # One of four: (num, val), (bit, val), (byte, val), (SPECIAL, val),
                # TODO Possibly add a fifth one to say number of these fields dependent on previous
                # field value or just an integer??
                if len(item) == 2:
                    if type(item[0]) is int:
                        if type(item[1]) is int or type(item[1]) is bytes:
                            # Field with specified size of bits and value
                            fields.append(Field(name, item[0], item[1]))
                        else:
                            raise InvalidValue(type(item[1]))
                    elif type(item[0]) is str:
                        if item[0] in CONSTANTS:
                            # Field is a special type, with a specified value.
                            fields.append(Field(name, item[0].lower(), item[1]))
                        elif type(item[1]) is int or type(item[1]) is bytes:
                            if re.fullmatch(r"[1-9][0-9]*b", item[0]):
                                # Specifying number of bits and value
                                fields.append(Field(name, int(item[0][:-1]), item[1]))
                            elif re.fullmatch(r"[1-9][0-9]*B", item[0]):
                                # Specifying number of bytes and value
                                fields.append(Field(name, int(item[0][:-1])*8, item[1]))
                            elif type(item[1]) is bytes and item[0].lower() == 'auto':
                                fields.append(Field(name, len(item[1]), item[1]))
                            else:
                                # Unrecognized string for size.
                                raise InvalidSize(item[0], msg="Invalid string for size")
                        else:
                            # Unrecognized size or field.
                            raise InvalidField(item)
                    else:
                            # Invalid size type.
                            raise InvalidSize(type(item[0]))
                else:
                    # Too many values in tuple. #TODO Let user enter 3rd argument for variable number fields.
                    raise InvalidField(item, msg="Invalid field. Tuples must have 2-elements, but recieved:")
            elif type(item) is bytes:
                fields.append(Field(name, len(item), item))
            else:
                # Unregonized field.
                raise InvalidField(item)
        return fields
