import socket
import struct

from new_deserialize import Deserialize
from deserialize import Deserialize1


sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))
flags = 1 << 8
req=struct.pack('!HHHHHH', 17, flags, 1, 0,0,0)
parts = 'justinroosenschoon.com'.split('.')
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
sd.send(req+q2)
rsp = sd.recv(1024)
pack = Deserialize(rsp, {
  # name of field: ('# Bytes', 'formating string', 'variable')
  # 'jack': () => 1 bit, no formating, no variable
  'pid': ('1B'),
  'pflags': ('1B'),
  'qcnt': ('1B', '','QUESTIONS'),
  'acnt': ('1B', '','ANSWERS'),
  'ncnt': ('1B'),
  'mcnt': ('1B'),
  'QUESTIONS': {  
    'qname': ('13b', Deserialize.HOST),
    'qtype': ('1B'),
    'qclass': ('1B')
  },
  'ANSWERS': {
    'name': ('1B'),
    'type': ('1B'),
    'class': ('1B'),
    'ttl': ('2B'), 
    'data_length': ('1B'), 
    'address': ('2B', Deserialize.IPv4), 
  }
})

pack_working = Deserialize1(rsp)


print(pack.get_field('pid'))
print(pack.get_field('pflags'))
print(pack.get_field('qcnt'))
print(pack.get_field('acnt'))
print(pack.get_field('ncnt'))
print(pack.get_field('mcnt'))

print(pack_working.getHeader())