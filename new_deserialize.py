from functools import reduce
import struct
from field import Field


def read_bit_string(str):
    if str == "":
      return [1, 'b']
    size = ''
    format = ''
    # convert string into useful info
    for c in list(str):
      if(c.isnumeric()):
        size += c
      else:
        format = c
    return [int(size), format]

def bytes_to_bits(bytes):
  binary_string = ''
  for b in list(bytes):
    hex_as_binary = bin(b)
    padded_binary = hex_as_binary[2:].zfill(8)
    binary_string += padded_binary
  return binary_string

class Deserialize: 
  __sizes = {
    'b': 1, # bit
    'B': 2  # byte
  }
  __struct_sizes = {
    'b': 'b',
    'B': 'H'
  }

  def __init__(self, packet, data):
    self.packet = packet
    self.data = data
    self.fields = []
    self.variables = {}
    self.readPacket()

  def __read_portion(self, index, name, size, format, variable):
    length = size * self.__sizes[format]
    new_index = index+length

    struct_str = '!'
    for i in range(0,size):
      struct_str += self.__struct_sizes[format]

    val = struct.unpack(struct_str, self.packet[index:new_index])

    if 'variable' in locals() and len(variable) > 0:
      self.variables[variable] = val[0]

    f = Field(name, length, val[0])

    return [new_index, f]  

  def readPacket(self):
    index = 0
    for name, stuff in self.data.items():
      if(type(stuff) == dict):
        for i in range(0,self.variables[name]):
          data = []
          for sub_name, sub_stuff in stuff.items():
            (size, format) = read_bit_string(sub_stuff)
            (new_index, f) = self.__read_portion(index, sub_name, size, format, "")
            data.append(f)
            index = new_index
        self.fields.append({name: data})
      else: 
        if(type(stuff) == tuple):
          (format_str, variable) = stuff
          (size, format) = read_bit_string(format_str)
        else:
          (size, format) = read_bit_string(stuff)
          variable = ""
        (new_index, f) = self.__read_portion(index, name, size, format, variable)
        self.fields.append(f)
        index = new_index

  def get_field(self, field_name):
          for f in self.fields:
              if f.name.lower() == field_name.lower():
                  return f
          return None
  

