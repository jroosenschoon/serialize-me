from collections import Iterable

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
            temp = ""
            if field.size == 1:
                b_array += str(field.value)
                temp += str(field.value)
            else:
                b_array += "0" * (field.size - len(bin(field.value)[2:])) + bin(field.value)[2:]
                temp += "0" * (field.size - len(bin(field.value)[2:])) + bin(field.value)[2:]
            print(field.name, len(temp), temp)

        print(len(b_array))

        print(b_array)
        print(self.bits_to_bytes(b_array))




    def extract_fields(self):
        for name, stuff in self.data.items():
            if stuff == ():
                field = Field(name=name, value=0, size=1)
                self.fields.append(field)
            elif isinstance(stuff, int):
                field = Field(name=name, value=0, size=stuff)
                self.fields.append(field)
            elif isinstance(stuff[0], str):
                if "b" in stuff[0] or "bit" in stuff[0].lower():
                    size = int(stuff[0][:stuff[0].lower().index("b")])
                    print(":", name, size)
                    # TODO check if value can fit in specified bits.
                    field = Field(name=name, value=stuff[1], size=size)
                    self.fields.append(field)
                elif "B" in stuff[0] or "byte" in stuff[0].lower():
                    size = int(stuff[0][:stuff[0].lower().index("b")])*8
                    # TODO check if value can fit in specified bits.
                    field = Field(name=name, value=stuff[1], size=size)
                    self.fields.append(field)
                elif isinstance(stuff[0], int):
                    # TODO check if value can fit in specified bits.
                    field = Field(name=name, value=stuff[1], size=stuff[0])
                    self.fields.append(field)
            elif isinstance(stuff, str):
                if "b" in stuff or "bit" in stuff.lower():
                    size = int(stuff[:stuff.lower().index("b")])
                    print(":", name, size)
                    # TODO check if value can fit in specified bits.
                    field = Field(name=name, value=stuff[1], size=size)
                    self.fields.append(field)
                elif "B" in stuff or "byte" in stuff.lower():
                    size = int(stuff[:stuff.lower().index("b")])*8
                    # TODO check if value can fit in specified bits.
                    field = Field(name=name, value=0, size=size)
                    self.fields.append(field)
