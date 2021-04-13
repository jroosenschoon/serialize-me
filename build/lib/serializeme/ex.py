from deserialize import Deserialize, NULL_TERMINATE, HOST, IPv4

import socket
import struct


sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))
flags = 1 << 8
req = struct.pack('!HHHHHH', 17, flags, 1, 0, 0, 0)
parts = 'google.com'.split('.')
q = b''
q2 = b''
for part in parts:
    q += bytes([len(part)]) + part.encode()
    q2 += bytes([len(part)]) + part.encode()
q += b'\0\0\1\0\1'
q2 += b'\0\0\x1c\0\1'
# If you want to test:
# q = IPv4
# q2 = IPv6
sd.send(req + q)
rsp = sd.recv(1024)

pack = Deserialize(rsp, {
    # name of field: ('# Bytes', 'formating string', 'variable')
    # 'jack': () => 1 bit, no formating, no variable
    'pid': ('2B'),
    'pflags': ('2B'),
    'qcnt': ('2B'),
    'acnt': ('2B', '', 'ANSWERS'),
    'ncnt': ('2B'),
    'mcnt': ('2B'),
    'qname': (NULL_TERMINATE, HOST),
    'qtype': ('2B'),
    'qclass': ('2B'),
    'ANSWERS': {
        'name': ('2B'),
        'type': ('2B'),
        'class': ('2B'),
        'ttl': ('4B'),
        'data_length': ('2B'),  # TO DO - variable length for this stuff
        'address': ('4B', IPv4),
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
print('answers', pack.get_field('ANSWERS').value)
answers = pack.get_field('ANSWERS').value
print('num ans => ', len(answers))
for answer in answers:
    for item in answer:
        print(item.name, item.value)
