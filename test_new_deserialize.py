import socket
import struct

from new_deserialize import Deserialize
from deserialize import Deserialize1


sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))
flags = 1 << 8
req=struct.pack('!HHHHHH', 17, flags, 1, 0,0,0)
parts = 'jackgisel.com'.split('.')
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
  'pid': ('1B'),
  'pflags': ('1B'),
  'qcnt': ('1B'),
  'acnt': ('1B'),
  'ncnt': ('1B', 'ANSWER'),
  'mcnt': ('1B'),
  # 'ANSWER': {
  #   'ip_address': ('16B') 
  # }
})

pack_working = Deserialize1(rsp)
print(pack_working.getHeader())