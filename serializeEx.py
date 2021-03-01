from serialize import Serialize


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
            "qname": "google.com",
            "qtype": 16,
            "qclass": 16
            })




for field in dns_packet.fields:
    print(field)


print()

id = dns_packet.get_field("id")
print(id.value)

print(dns_packet.packetize())