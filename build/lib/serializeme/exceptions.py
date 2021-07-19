class InvalidIPv4Address(Exception):
    """
    Exception raised for invalid IPv4 addresses.
    Attributes:
        ipv4: IPv4 address that triggered the error.
        msg : Explanation of the error.
    """
    def __init__(self, ipv4, msg="Invalid IPv4 Address"):
        self.ipv4 = ipv4
        self.msg = msg
    
    def __str__(self):
        return "{}: {}".format(self.msg, self.ipv4)

class ValueTooBig(Exception):
    """
    Exception raised for trying to fit a value that cannot be fit in the specified
      number of bytes or bits.
    Attributes:
        size : Specified size user entered.
        value: Value user tried to fit in that size, but was too big. 
        unit : bit or byte, depending on how size was specified.
        msg  : Explanation of the error.
    """
    def __init__(self, size, value, unit, msg="Cannot fit in"):
        self.size  = size
        self.value = value
        self.unit = unit
        self.msg = msg
    
    def __str__(self):
        return "{} {} {} {}".format(self.value, self.msg, self.size, self.unit)

class InvalidValue(Exception):
    """
    Exception raised for invalid values for Field.py.
    Attributes:
        value: value that triggered the error.
        msg : Explanation of the error.
    """
    def __init__(self, value, msg="Invalid type for value. Expecting int or bytes. Received"):
        self.value = value
        self.msg = msg
    
    def __str__(self):
        return "{}: {}".format(self.msg, self.value)

class InvalidSize(Exception):
    """
    Exception raised for invalid sizes for Field.py.
    Attributes:
        size: size that triggered the error.
        msg : Explanation of the error.
    """
    def __init__(self, size, msg="Invalid type for size. Expecting str, int, or bytes. Received"):
        self.size = size
        self.msg = msg
    
    def __str__(self):
        return "{}: {}".format(self.msg, self.size)

class InvalidField(Exception):
    """
    Exception raised for an invalid field for Field.py.
    Attributes:
        item: What was used to trigger error.
        msg  : Explanation of the error.
    """
    def __init__(self, item, msg="Invalid Field. Recieved"):
        self.item = item
        self.msg = msg
    
    def __str__(self):
        return "{}: {}".format(self.msg, self.item)

class FieldNotFound(Exception):
    """
    Exception raised when user tries to access nonexistent field.
    Attributes:
        name: name of field user tried to access, but does not exist.
        msg : Explanation of the error.
    """
    def __init__(self, name, msg="Field not found."):
        self.name = name
        self.msg = msg
    
    def __str__(self):
        return "{} -> {}".format(self.name, self.msg)
