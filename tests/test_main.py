import serializeme
import socket

from serializeme import Serialize, Deserialize

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

sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))

sd.send(dns_packet.packetize())

rsp = sd.recv(1024)

pack = Deserialize(rsp, {
    # name of field: ('# Bytes', 'formatting string', 'variable')
    # 'jack': () => 1 bit, no formating, no variable
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
        'data_length': ('2B'),  # TO DO - variable length for this stuff
        'address': ('4B', serializeme.IPv4),
    }
})

print('pid', pack.get_field('pid').value)
print('pflags', pack.get_field('pflags').value)
print('qcnt', pack.get_field('qcnt').value)
print('acnt', pack.get_field('acnt').value)
print('ncnt', pack.get_field('ncnt').value)
print('qname', pack.get_field('qname').value)
print('qtype', pack.get_field('qtype').value)
print('qclass', pack.get_field('qclass').value)
# print('answers', pack.get_field('ANSWERS').value)
answers = pack.get_field('ANSWERS').value
print('num ans => ', len(answers))
for answer in answers:
    for item in answer:
        print(item.name, item.value)
