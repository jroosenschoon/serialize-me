
NULL_TERMINATE = "null_terminate"
PREFIX_LENGTH  = "prefix_length"
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"

VAR_PREFIXES = [NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM]


class Field:
    def __init__(self, name, size, value=0):
        self.name = name
        self.size = size
        self.value = value

    def to_binary(self):
        if self.size not in VAR_PREFIXES:
            return "0" * (self.size - len(bin(self.value)[2:])) + bin(self.value)[2:]

    def to_hex(self):
        if self.size not in VAR_PREFIXES:
            return "0" * int((self.size - len(bin(self.value)[2:]))/4) + hex(int(bin(self.value)[2:], 2))[2:]

    def __str__(self):
        if self.size == "null_terminate":
            return "Field [name: " + self.name + ", Null terminated, Value: " + str(self.value) + "]"
        elif self.size == "prefix_length":
            return "Field [name: " + self.name + ", Length prefixed, Value: " + str(self.value) + "]"
        return "Field [name: " + self.name + ", Num bits: " + str(self.size) + ", Value: " + str(self.value) + "]"

