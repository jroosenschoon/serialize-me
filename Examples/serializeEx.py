from serializeme import serialize

#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# 1 | ID |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# 2 | QR | Opcode | AA | TC | RD | RA | Z | RCODE |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# 3 | QDCOUNT |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# 4 | ANCOUNT |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# 5 | NSCOUNT |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# 6 | ARCOUNT |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

# {
#     "name" : (size, value)
#     "name" : size    # Value defaults to 0
#     "name": ()   # size  1bit with 0 as value
#
# }
# Size - a number (defaults to num bits), "2b" for 2 bits or "2B" for 2 bytes
# -
# NULL_TERMINATE = "null_terminate"
# PREFIX_LENGTH  = "prefix_length"
# PREFIX_LEN_NULL_TERM = "prefix_len_null_term"

# serialize.NULL_TERMINATE or "null_terminate"

dns_packet = serialize.Serialize({
            "id": (16, 17),
            "qr": (),
            "opcode": 4,
            "aa": (),
            "tc": (),
            "rd": (1, 1),
            "ra": (),
            "z": 3,
            "rcode": 4,
            "qdcount": ("2B", 1),
            "ancount": "16b",
            "nscount": 16,
            "arcount": 16,
            "qname": (serialize.PREFIX_LEN_NULL_TERM, ("google", "com")),
            "qtype": (16, 1),
            "qclass": (16, 1)
            })


print(dns_packet)


print(dns_packet.get_field("id"))
print(dns_packet.get_field("id").to_binary())
print(dns_packet.get_field("id").to_hex())

# id = dns_packet.get_field("id")
# print(id.value)

# print(dns_packet.packetize())

# sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sd.connect(('8.8.8.8', 53))

# parts = "facebook.com".split(".")
# q = b''
# for part in parts:
#     q += bytes([len(part)]) + part.encode()
#
# # q += b'\0\0\1\0\1'
# q += b'\0\0' + bytes.fromhex("1c") + b'\0\1'


# sd.send(dns_packet.packetize())


