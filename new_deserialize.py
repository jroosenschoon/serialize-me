import struct
from functools import reduce

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
    'b': 1,
    'B': 4
  }

  def __init__(self, packet, data):
    self.packet = packet
    self.data = data
    self.fields = []
    self.variables = {}
    self.readPacket()

    

  def readPacket(self):
    index = 0
    # self.packet => bit array
    bits = bytes_to_bits(self.packet)
    print(bits)
    print(len(bits))
    for name, stuff in self.data.items():
      if(type(stuff) == dict):
        print(stuff)
      elif(type(stuff) == tuple):
        (format_str, variable) = stuff
        (size, format) = read_bit_string(format_str)
         # this should be set equal to the int value of the result of this read
        self.variables[variable] = 1
      else:
        # '' => defaults to 1 bit
        if(stuff == ''):
          size = 1
          format = 'b'
        else: 
          (size, format) = read_bit_string(stuff)
        print(name, size, format)

  

