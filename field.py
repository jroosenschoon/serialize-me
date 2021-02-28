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
        return "Field [name: " + self.name + ", Num bits: " + str(self.size) + ", Value: " + str(self.value) + "]"

