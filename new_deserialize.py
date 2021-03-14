import struct

from functools import reduce
from field import Field

class Deserialize:
  # types of formatting
  HOST = "host"
  IPv4  = "IPv4"
  IPv6 = "IPv6"
  NULL_TERMINATE = "null_terminate" # two \x00\x00
  PREFIX_LENGTH  = "prefix_length"
  PREFIX_LEN_NULL_TERM = "prefix_len_null_term" 

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
    self.__readPacket()

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

  def __read_bit_string(self,bit_string):
    if bit_string == "":
      return [1, 'b']
    size = ''
    format = ''
    # convert string into useful info
    for c in list(bit_string):
      if(c.isnumeric()):
        size += c
      else:
        format = c
    return [int(size), format]

  def __format_hostname(self, bits):
    dirty_host = bits.decode("utf-8").split('\x03')
    clean_host = '.'.join(dirty_host).replace('\x01', '').replace('\x00', '')
    return clean_host

  def __format_ipv4(self, bits):
    address = bits.decode('utf-8')
    print(address)
    s = str(hex(address))[2:]
    ip_address = ('.'.join(str(int(i, 16)) for i in ([s[i:i+2] for i in range(0, len(s), 2)])))
    return ip_address

  def __format_ipv6(self, bits):
    return bits

  def __handle_custom_formatting(self, format, bits):
    if format == self.IPv4:
      return self.__format_ipv4(bits)
    elif format == self.IPv6:
      return self.__format_ipv6(bits)
    elif format == self.HOST:
      return self.__format_hostname(bits)
    else:
      return None

  def __readPacket(self):
    index = 0
    print(self.packet)
    for name, stuff in self.data.items():
      if(type(stuff) == dict):
        for i in range(0,self.variables[name]):
          data = []
          for sub_name, sub_stuff in stuff.items():
            if(type(sub_stuff) == tuple):
              (format_str, value_format) = sub_stuff
              (size, format) = self.__read_bit_string(format_str)
              length = size * self.__sizes[format]
              new_index = index+length
              dirty_bytes = self.packet[index:new_index]
              print(index, new_index, dirty_bytes)
              print(self.__handle_custom_formatting(value_format, dirty_bytes))
            else:
              (size, format) = self.__read_bit_string(sub_stuff)
              (new_index, f) = self.__read_portion(index, sub_name, size, format, "")
            data.append(f)
            index = new_index
        self.fields.append({name: data})
      else: 
        if(type(stuff) == tuple):
          (format_str, value_format, variable) = stuff
          (size, format) = self.__read_bit_string(format_str)
        else:
          (size, format) = self.__read_bit_string(stuff)
          variable = ""
        (new_index, f) = self.__read_portion(index, name, size, format, variable)
        print(index, new_index, f.value)
        self.fields.append(f)
        index = new_index

  def get_field(self, field_name):
    for f in self.fields:
      if f.name.lower() == field_name.lower():
        return f
      # elif if variables
    return None
  

