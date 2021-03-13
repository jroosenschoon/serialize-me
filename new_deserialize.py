from functools import reduce
import struct
from field import Field


def read_bit_string(str):
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
  sizes = {
    'b': 1, #bit
    'B': 2 #byte
  }
  struct_sizes = {
    'b': 'b',
    'B': 'H'
  }

  def __init__(self, packet, data):
    self.packet = packet
    self.data = data
    self.fields = []
    self.variables = {}
    self.readPacket()

    

  def readPacket(self):
    index = 0
    for name, stuff in self.data.items():
      if(type(stuff) == tuple):
        (format_str, variable) = stuff
        (size, format) = read_bit_string(format_str)
      
        # handle the variable
        # self.variables[variable] = 1
      else:
        if(stuff == ''):
          size = 1
          format = 'b'
        else: 
          (size, format) = read_bit_string(stuff)

      length = size * self.sizes[format]
      new_index = index+length

      struct_str = '!'
      for i in range(0,size):
        struct_str += "H"

      val = struct.unpack(struct_str, self.packet[index:new_index])

      f = Field(name, length, val[0])
      self.fields.append(f)
      index = new_index


  

