from serialize import *
import socket

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

dns_packet = Serialize({
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
            "qname": (PREFIX_LEN_NULL_TERM, ("google", "com")),
            "qtype": (16, 1),
            "qclass": (16, 1)
            })


# for field in dns_packet.fields:
#     print(field)

# print()

# id = dns_packet.get_field("id")
# print(id.value)

# print(dns_packet.packetize())

sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))

# parts = "facebook.com".split(".")
# q = b''
# for part in parts:
#     q += bytes([len(part)]) + part.encode()
#
# # q += b'\0\0\1\0\1'
# q += b'\0\0' + bytes.fromhex("1c") + b'\0\1'


# sd.send(dns_packet.packetize())

