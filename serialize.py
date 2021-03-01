import re

from field import Field


class Serialize:
    # TODO Need variable-length data. eg the domain name for DNS.
    def __init__(self, data):
        self.data = data

        self.fields = []

        self.extract_fields()

    def bits_to_bytes(self, bit_str):
        return int(bit_str, 2).to_bytes((len(bit_str) + 7) // 8, byteorder='big')

    def packetize(self):
        b_array = ""
        for field in self.fields:
            if field.size == 1:
                b_array += str(field.value)
            else:
                if field.size != "vary":
                    b_array += "0" * (field.size - len(bin(field.value)[2:])) + bin(field.value)[2:]
                else:
                    b_array += ' '.join(format(ord(x), 'b') for x in field.value) + "0"*8
                    #TODO add variable length field size to byte array. (convert value to binary and add it?)
        return b_array

    def get_field(self, field_name):
        for f in self.fields:
            if f.name.lower() == field_name.lower():
                return f
        return None

    # TODO check if value can fit in specified bits.
    def checkBitSize(self, value, num_bits):
        pass

    def extract_fields(self):
        for name, stuff in self.data.items():
            if stuff == ():  # Empty tuple == 1 bit, value of 0
                self.fields.append(Field(name=name, value=0, size=1))
            elif isinstance(stuff, int):  # int == specified value, value of 0
                self.fields.append(Field(name=name, value=0, size=stuff))
            elif isinstance(stuff, str):  # str == specified value, value of 0
                pattern = re.compile("[0-9][bB]")
                if pattern.match(stuff):
                    if "b" in stuff:
                        size = int(stuff[:stuff.lower().index("b")])
                        # TODO check if value can fit in specified bits.
                        self.fields.append(Field(name=name, value=0, size=size))
                    elif "B" in stuff:
                        size = int(stuff[:stuff.lower().index("b")]) * 8
                        # TODO check if value can fit in specified bits.
                        self.fields.append(Field(name=name, value=0, size=size))
                else:
                    self.fields.append(Field(name=name, value=stuff, size="vary"))
            elif isinstance(stuff, tuple) or isinstance(stuff, list):  # specified value and size.
                if isinstance(stuff[0], str):
                    # TODO check if value can fit in specified bits.
                    if "b" in stuff[0]:
                        size = int(stuff[0][:stuff[0].lower().index("b")])
                        # TODO check if value can fit in specified bits.
                        self.fields.append(Field(name=name, value=stuff[1], size=size))
                    elif "B" in stuff[0]:
                        size = int(stuff[0][:stuff[0].lower().index("b")]) * 8
                        # TODO check if value can fit in specified bits.
                        self.fields.append(Field(name=name, value=stuff[1], size=size))
                elif isinstance(stuff[0], int):
                    # TODO check if value can fit in specified bits.
                    self.fields.append(Field(name=name, value=stuff[1], size=stuff[0]))



