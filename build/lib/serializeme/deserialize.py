import struct

from serializeme.field import Field

HOST = "host"
IPv4 = "IPv4"
IPv6 = "IPv6"
NULL_TERMINATE = "null_terminate"  # two \x00\x00
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"
PREFIX_LENGTH = "prefix_length"  # \x03 = length of 3


class Deserialize:
    __sizes = {
        'b': 1,  # bit
        'B': 1  # byte
    }
    __struct_sizes = {
        'b': 'b',
        'B': {
            1: 'B',
            2: 'H',
            4: 'L',
            8: 'Q'
        }
    }

    def __init__(self, packet, data):
        self.packet = packet
        self.data = data
        self.fields = []
        self.variables = {}
        self.__readPacket()

    def __read_portion(self, index, name, size, format, variable):
        length = size * self.__sizes[format]
        new_index = index + length
        struct_str = '!'

        if size in [1, 2, 4]:
            struct_str += self.__struct_sizes[format][size]
        else:
            for i in range(0, size):
                struct_str += 'B'

        val = struct.unpack(struct_str, self.packet[index:new_index])

        if len(val) > 1:
            val = ''.join(chr(i) for i in val)
        else:
            val = val[0]

        if 'variable' in locals() and len(variable) > 0:
            self.variables[variable] = val

        f = Field(name, length, val)

        return [new_index, f]

    def __read_bit_string(self, bit_string):
        if bit_string == "":
            return [1, 'b']
        size = ''
        format = ''
        # convert string into useful info
        for c in list(bit_string):
            if (c.isnumeric()):
                size += c
            else:
                format = c
        return [int(size), format]

    def __format_hostname(self, bites):
        temp_str = []
        for i in range(1, len(bites)):
            char = bites[i:i+1].decode()
            if char.isprintable():
                temp_str.append(char)
            else:
                temp_str.append('.')
        return ''.join(temp_str)

    def __format_ipv4(self, bites):
        address = bites.hex()
        s = str(address)
        ip_address = ('.'.join(str(int(i, 16))
                      for i in ([s[i:i + 2] for i in range(0, len(s), 2)])))
        return ip_address

    def __format_ipv6(self, bites):
        s = str(bites.hex())
        ip_address = ':'.join(s[i:i + 4] for i in (range(0, 16, 4)))
        return ip_address

    def __handle_custom_formatting(self, format, bits):
        if format == IPv4:
            return self.__format_ipv4(bits)
        elif format == IPv6:
            return self.__format_ipv6(bits)
        elif format == HOST:
            return self.__format_hostname(bits)
        else:
            return None

    def __readPacket(self):
        index = 0
        for name, stuff in self.data.items():
            if '!!' in name:
                # Handle the bit issue
                (size, n) = self.__read_bit_string(name[2:])
                new_index = index + size
                bits = bin(int.from_bytes(
                    self.packet[index:new_index], byteorder="big")).strip('0b')
                while len(bits) < size * 8:
                    bits = "0" + bits
                ind = 0
                for thing in stuff:
                    (s, form) = self.__read_bit_string(stuff[thing])
                    new_ind = ind + s
                    val = bits[ind:new_ind]
                    val = int(val, 2)
                    fp = Field(thing, s, val)
                    self.fields.append(fp)
                    ind = new_ind
                index = new_index

            elif type(stuff) == dict:
                old_index = index  # save for length
                all_data = []
                for i in range(0, self.variables[name]):
                    data = []
                    for sub_name, sub_stuff in stuff.items():
                        if type(sub_stuff) == tuple:
                            (format_str, value_format) = sub_stuff
                            if format_str == NULL_TERMINATE or format_str == PREFIX_LEN_NULL_TERM:
                                null_count = 0
                                front = index + 1
                                back = index
                                byte_queue = b''
                                while null_count < 1:
                                    if self.packet[back:front] == b'\x00':
                                        null_count += 1
                                    else:
                                        byte_queue += self.packet[back:front]
                                    front += 1
                                    back += 1
                                val = self.__handle_custom_formatting(
                                    value_format, byte_queue)
                                f = Field(sub_name, format_str, val)
                                new_index = back  # dont forgot to update index for variable length
                            elif format_str == PREFIX_LENGTH:
                                size = int.from_bytes(
                                    self.packet[index:index+1], "big")
                                index = index + 1
                                (new_index, f) = self.__read_portion(
                                    index, name, size, 'B', '')
                            else:
                                (size, format) = self.__read_bit_string(format_str)
                                length = size * self.__sizes[format]
                                new_index = index + length
                                dirty_bytes = self.packet[index:new_index]
                                val = self.__handle_custom_formatting(
                                    value_format, dirty_bytes)
                                f = Field(sub_name, new_index - index, val)
                        else:
                            if sub_stuff == NULL_TERMINATE or sub_stuff == PREFIX_LEN_NULL_TERM:
                                null_count = 0
                                front = index + 1
                                back = index
                                byte_queue = b''
                                while null_count < 1:
                                    if self.packet[back:front] == b'\x00':
                                        null_count += 1
                                        break
                                    else:
                                        byte_queue += self.packet[back:front]
                                    front += 1
                                    back += 1
                                if value_format != "":
                                    val = self.__handle_custom_formatting(
                                        value_format, byte_queue)
                                else:
                                    val = self.__format_hostname(byte_queue)
                                f = Field(sub_name, sub_stuff, val)
                                new_index = back  # dont forgot to update index for variable length
                            elif sub_stuff == PREFIX_LENGTH:
                                size = int.from_bytes(
                                    self.packet[index:index+1], "big")
                                index = index + 1
                                (new_index, f) = self.__read_portion(
                                    index, name, size, 'B', '')
                            else:
                                (size, format) = self.__read_bit_string(sub_stuff)
                                (new_index, f) = self.__read_portion(
                                    index, sub_name, size, format, "")
                        data.append(f)
                        index = new_index
                    all_data.append(data)
                custom_length = str(index - old_index) + 'B'
                var_field = Field(name, custom_length, all_data)
                self.fields.append(var_field)
            else:
                if (type(stuff) == tuple):
                    format_str = stuff[0]
                    value_format = stuff[1]
                    variable = stuff[2] if len(stuff) > 2 else ''
                    # handle variable length
                    if format_str == NULL_TERMINATE or format_str == PREFIX_LEN_NULL_TERM:
                        null_count = 0
                        front = index + 1
                        back = index
                        byte_queue = b''
                        while null_count < 1:
                            if (self.packet[back:front] == b'\x00'):
                                null_count += 1
                            else:
                                byte_queue += self.packet[back:front]
                            front += 1
                            back += 1
                        val = self.__handle_custom_formatting(
                            value_format, byte_queue)
                        f = Field(name, str(back - index) + 'B', val)
                        new_index = back
                    elif format_str == PREFIX_LENGTH:
                        if value_format != None:
                            size = int.from_bytes(
                                self.packet[index:index+1], "big")
                            val = self.__handle_custom_formatting(
                                value_format, self.packet[index:index+size+1])
                            f = Field(name, str(size) + 'B', val)
                            new_index = index + size + 1
                        else:
                            size = int.from_bytes(
                                self.packet[index:index+1], "big")
                            index = index + 1
                            (new_index, f) = self.__read_portion(
                                index, name, size, 'B', variable)
                    else:
                        if value_format in [HOST, IPv4, IPv6]:
                            (size, format) = self.__read_bit_string(format_str)
                            c = 0
                            front = index + 1
                            back = index
                            byte_queue = b''
                            while c < size:
                                byte_queue += self.packet[back:front]
                                front += 1
                                back += 1
                                c = c + 1
                            val = self.__handle_custom_formatting(
                                value_format, byte_queue)
                            f = Field(name, str(back - index) + 'B', val)
                            new_index = back
                        else:
                            (size, format) = self.__read_bit_string(format_str)
                            (new_index, f) = self.__read_portion(
                                index, name, size, format, variable)
                else:
                    if stuff == NULL_TERMINATE or stuff == PREFIX_LEN_NULL_TERM:
                        null_count = 0
                        front = index + 1
                        back = index
                        byte_queue = b''
                        while null_count < 1:
                            if (self.packet[back:front] == b'\x00'):
                                null_count += 1
                            else:
                                byte_queue += self.packet[back:front]
                            front += 1
                            back += 1
                        val = self.__handle_custom_formatting(
                            value_format, byte_queue)
                        f = Field(name, str(back - index) + 'B', val)
                        new_index = back
                    elif stuff == PREFIX_LENGTH:
                        size = int.from_bytes(
                            self.packet[index:index+1], "big")
                        index = index + 1
                        (new_index, f) = self.__read_portion(
                            index, name, size, 'B', '')
                    else:
                        (size, format) = self.__read_bit_string(stuff)
                        (new_index, f) = self.__read_portion(
                            index, name, size, format, '')

                self.fields.append(f)
                index = new_index

    def get_field(self, field_name):
        for f in self.fields:
            if f.name.lower() == field_name.lower():
                return f
            # elif if variables
        return None

    def get_value(self, field_name):
        return self.get_field(field_name).value

# TODO: Fix test cases into file lol


# pack = Deserialize(b'\x32\xff\xff\xff\xff', {
#     'id': '1B',
#     "dest": ('4B', IPv4)
# })
# print(pack.get_field('id'))

# print(pack.get_field('dest'))


# pack = Deserialize(b'\x05\x01\x00\x03\x0ewww.google.com\x00P', {
#     "VER": "1B",
#     "CMD": "1B",
#     "RSV": "1B",
#     "ATYP": "1B",
#     "DADDR": (PREFIX_LENGTH, HOST),
#     "DPORT": "2B",
# })


# print(pack.get_field('DADDR'))
# print(pack.get_field('DPORT'))
# rsp = b'\x01\x06cs158b\x08Pa55word'

# pck = Deserialize(rsp, {
#     "VER": "1B",
#     "ID": PREFIX_LENGTH,
#     "PW": PREFIX_LENGTH
# })

# print(pck.get_field("VER").value)
# print(pck.get_field("ID").value)
# print(pck.get_field("PW").value)

# rsp = b'\x01\x03\x00\x01\x02'

# pck = Deserialize(rsp, {
#     "VER": "1B",
#     "NAUTHS": ('1B', "", "AUTHS"),
#     "AUTHS": {
#         'val': '1B'
#     }
# })

# print(pck.get_value("VER"))
# print(pck.get_value("NAUTHS"))
# print(pck.get_value("AUTHS"))

# pck = Deserialize(b'\x41\x33', {
#     "!!2B": {'b0': '',
#              'b1': '3b',
#              'b2': '4b',
#              'b3': '4b',
#              'b4': '4b',
#              }
# })

# print(pck.get_value("b0"))
# print(pck.get_value("b1"))
# print(pck.get_value("b2"))
# print(pck.get_value("b3"))
# print(pck.get_value("b4"))

# # DNS example
# dns_request = {
#     "ID": "2B",
#     "!!2B": {
#         'QR': '1b',
#         'OPCODE': '4b',
#         'AA': '1b',
#         'TC': '1b',
#         'RD': '1b',
#         'RA': '1b',
#         "Z": "3b",
#         "RCODE": "4b",
#     },
#     "QDCOUNT": ("2B", "", "QUERIES"),
#     "ANCOUNT": "2B",
#     "NSCOUNT": "2B",
#     "ARCOUNT": "2B",
#     "QUERIES": {
#         "QNAME": PREFIX_LEN_NULL_TERM,
#         "QTYPE": "2B",
#         "QCLASS": "2B"
#     }
# }

# pck = Deserialize(b'\xccD\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x06google\x03com\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08\xd9\xd7\xa3\xbf\xe7\xb3\xae\xb9', dns_request)
# print(pck.get_value('QUERIES')[0][0].value)
# pck = Deserialize(b'\x10\xf0\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x011\x011\x0216\x03172\x07in-addr\x04arpa\x00\x00\x0c\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08\xdc\x10\xd7\xca"\xf7\xc4\xb7', dns_request)
# print(pck.get_value('QUERIES')[0][0].value)
