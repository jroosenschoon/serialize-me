import re

from serializeme.field import Field

NULL_TERMINATE = "null_terminate"
PREFIX_LENGTH  = "prefix_length"
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"

VAR_PREFIXES = [NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM]


class Serialize:
    def __init__(self, data):
        self.data = data

        self.fields = []

        self.__extract_fields()

    # Helper
    def __bits_to_bytes(self, bit_str):
        bit_str = bit_str.replace(" ", "")
        return int(bit_str, 2).to_bytes((len(bit_str) + 7) // 8, byteorder='big')

    def packetize(self):
        bit_str = ""
        for field in self.fields:
            if field.size == 1:
                bit_str += str(field.value)
            else:
                if field.size not in [NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM]:
                    bit_str += "0" * (field.size - len(bin(field.value)[2:])) + bin(field.value)[2:]
                if field.size == PREFIX_LENGTH or field.size == PREFIX_LEN_NULL_TERM:
                    for f in field.value:
                        length_byte = "0" * (8-len(bin(len(f))[2:])) + bin(len(f))[2:]
                        bit_str += length_byte
                        bit_str += f
                elif field.size == NULL_TERMINATE:
                    bit_str += bin(field.value)[2:] + "0" * 8
                    bit_str += "0"*8
                if field.size == PREFIX_LEN_NULL_TERM:
                    bit_str += "0" * 8

        # Convert bit string to byte array.
        b_array = b''
        temp_byte = ""
        temp_word = ""
        for c in bit_str:
            if len(temp_byte) == 8:
                b_array += self.__bits_to_bytes(temp_byte)
                temp_byte = ""
            if c == "0" or c == "1":
                b_array += temp_word.encode()
                temp_word = ""
                temp_byte += c
            else:
                temp_word += c
        b_array += self.__bits_to_bytes(temp_byte)
        b_array += temp_word.encode()
        return b_array

    def get_field(self, field_name):
        for f in self.fields:
            if f.name.lower() == field_name.lower():
                return f
        return None

    # Helper
    def __check_bit_size(self, value, num_bits):
        is_fit = False
        if value <= 2 ** num_bits - 1:
            is_fit = True
        return is_fit

    # Helper
    def __extract_fields(self):
        for name, stuff in self.data.items():
            if stuff == ():  # Empty tuple == 1 bit, value of 0
                self.fields.append(Field(name=name, value=0, size=1))
            elif isinstance(stuff, int):  # int == specified value, value of 0
                self.fields.append(Field(name=name, value=0, size=stuff))
            elif isinstance(stuff, str):  # str == specified value, value of 0
                pattern = re.compile("[0-9]+[bB]")
                if pattern.match(stuff):
                    if "b" in stuff:
                        size = int(stuff[:stuff.lower().index("b")])
                        self.fields.append(Field(name=name, value=0, size=size))
                    elif "B" in stuff:
                        size = int(stuff[:stuff.lower().index("b")]) * 8
                        self.fields.append(Field(name=name, value=0, size=size))
                else:
                    self.fields.append(Field(name=name, value=stuff, size="vary"))
            elif isinstance(stuff, tuple) or isinstance(stuff, list):  # specified value and size.
                if isinstance(stuff[0], str):
                    if "b" in stuff[0]:
                        size = int(stuff[0][:stuff[0].lower().index("b")])
                        if not self.__check_bit_size(stuff[1], size):
                            raise Exception("error. " + str(stuff[1]) + " cannot be fit in " + str(size) + " bits.")
                        self.fields.append(Field(name=name, value=stuff[1], size=size))
                    elif "B" in stuff[0]:
                        size = int(stuff[0][:stuff[0].lower().index("b")]) * 8
                        if not self.__check_bit_size(stuff[1], size):
                            raise Exception("error. " + str(stuff[1]) + " cannot be fit in " + str(size) + " bits.")
                        self.fields.append(Field(name=name, value=stuff[1], size=size))
                    elif stuff[0].lower() == NULL_TERMINATE:
                        self.fields.append(Field(name=name, value=stuff[1], size=NULL_TERMINATE))
                    elif stuff[0].lower() == PREFIX_LENGTH:
                        self.fields.append(Field(name=name, value=stuff[1], size=PREFIX_LENGTH))
                    elif stuff[0].lower() == PREFIX_LEN_NULL_TERM:
                        self.fields.append(Field(name=name, value=stuff[1], size=PREFIX_LEN_NULL_TERM))
                elif isinstance(stuff[0], int):
                    if not self.__check_bit_size(stuff[1], stuff[0]):
                        raise Exception("error. " + str(stuff[1]) + " cannot be fit in " + str(stuff[0]) + " bits.")
                    self.fields.append(Field(name=name, value=stuff[1], size=stuff[0]))

    def __str__(self):
        s = ""
        for field in self.fields:
            if field.size not in VAR_PREFIXES:
                s += field.name + ": " + str(field.size) + " bits with value " + str(field.value) + ".\n"
            else:
                s += field.name + ": variable size: " + str(field.size) + ", with value " + str(field.value) + ".\n"

        return s