import serializeme
from serializeme import Serialize, Deserialize
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
            "qname": (serializeme.PREFIX_LEN_NULL_TERM, ("yahoo", "com")),
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

# Receive packet.
rsp = sd.recv(1024)

# Create format structure so we can grab all the fields of the response from the DNS server.
pack = Deserialize(rsp, {
    'pid': ('2B'),
    'pflags': ('2B'),
    'qcnt': ('2B'),
    'acnt': ('2B', '', 'ANSWERS'),
    'ncnt': ('2B'),
    'mcnt': ('2B'),
    'qname': (serializeme.NULL_TERMINATE, serializeme.HOST),
    'qtype': ('2B'),
    'qclass': ('2B'),
    'ANSWERS': {
        'name': ('2B'),
        'type': ('2B'),
        'class': ('2B'),
        'ttl': ('4B'),
        'data_length': ('2B'),
        'address': ('4B', serializeme.IPv4),
    }
})

# Print out all of the fields.
print('pid', pack.get_field('pid').value)
print('pflags', pack.get_field('pflags').value)
print('qcnt', pack.get_field('qcnt').value)
print('acnt', pack.get_field('acnt').value)
print('ncnt', pack.get_field('ncnt').value)
print('qname', pack.get_field('qname').value)
print('qtype', pack.get_field('qtype').value)
print('qclass', pack.get_field('qclass').value)
answers = pack.get_field('ANSWERS').value
print('num ans => ', len(answers))
for answer in answers:
    for item in answer:
        print(item.name, item.value)
