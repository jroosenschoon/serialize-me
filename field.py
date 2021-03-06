class Field:
    def __init__(self, name, size, value=0):
        self.name = name
        self.size = size
        self.value = value

    def to_binary(self):
        pass

    def to_hex(self):
        pass

    def __str__(self):
        if self.size == "null_terminate":
            return "Field [name: " + self.name + ", Null terminated, Value: " + str(self.value) + "]"
        elif self.size == "prefix_length":
            return "Field [name: " + self.name + ", Length prefixed, Value: " + str(self.value) + "]"
        return "Field [name: " + self.name + ", Num bits: " + str(self.size) + ", Value: " + str(self.value) + "]"
