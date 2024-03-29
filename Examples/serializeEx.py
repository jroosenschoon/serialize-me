import serializeme
from serializeme import Serialize
import socket

# We want to make a DNS packet. RFC1035 gives:
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
#  |                       ID                      |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
#  | QR | Opcode | AA | TC | RD | RA | Z | RCODE   |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
#  |                   QDCOUNT                     |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
#  |                   ANCOUNT                     |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
#  |                   NSCOUNT                     |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
#  |                   ARCOUNT                     |
#  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# And then the query has the below form which is added directly below the header.
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                                               |
# /                    QNAME                      /
# /                                               /
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    QTYPE                      |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    QCLASS                     |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

# We can create this packet structure with the following code. This will ask for google.com.
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
            "qname": (serializeme.PREFIX_LEN_NULL_TERM, ("google", "com")),
            "qtype": (16, 1),
            "qclass": (16, 1)
            })


# Print out packet
print(dns_packet)


# Get the ID field and show it as decimal, binary, and hex.
print(dns_packet.get_field("id"))
print(dns_packet.get_field("id").to_binary())
print(dns_packet.get_field("id").to_hex())

# Establish connection to Google's DNS server.
sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))

# Send bytes of dns_packet.
sd.send(dns_packet.packetize())


