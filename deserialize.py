import struct

class Deserialize1: 
  def __init__(self, packet):
    self.packet = packet
    self.header = {}
    self.query = {}
    self.answers = []
    self.ipv = 4
    self.readPacket()
  
  def readPacket(self):
    # Get headers
    head = struct.unpack('!HHHHHH', self.packet[0:12])
    self.header['id'] = head[0] 
    self.header['flags'] = head[1] 
    self.header['qcnt'] = head[2] 
    self.header['acnt'] = head[3]
    self.header['ncnt'] = head[4] 
    self.header['mcnt'] = head[5]
    # Get Query
    query = self.packet[13:26]
    dirty_host = query.decode("utf-8").split('\x03')
    clean_host = '.'.join(dirty_host).replace('\x01', '').replace('\x00', '')
    (qtype, qclass) = struct.unpack('!HH',self.packet[27:31])
    self.query['qname'] = clean_host
    self.query['qtype'] = qtype
    self.query['qclass'] = qclass

    if qtype == 1:
      self.ipv = 4
    elif qtype == 28:
      self.ipv = 6

    # Handle the correct query type (IPv4 / IPv6)
    if self.header['acnt'] > 0:
      ans_size = 16 if self.ipv == 4 else 28
      back = len(self.packet)
      front = back - ans_size
      for x in range(0, self.header['acnt']):
        if self.ipv == 4: 
          (name, atype, aclass,ttl,data_length, address) = struct.unpack('!HHHIHI',self.packet[front:back])
          s = str(hex(address))[2:]
          # format address into ip address
          ip_address = ('.'.join(str(int(i, 16)) for i in ([s[i:i+2] for i in range(0, len(s), 2)])))
        else:
          (name, atype, aclass,ttl,data_length, hi,lo) = struct.unpack('!HHHIHQQ',self.packet[front:back])
          s = str(hex(hi<<64 | lo))[2:]
          address = s
          ip_address = ':'.join(s[i:i+4] for i in (range(0, 16, 4)))

        # loop for multiple results
        back = front
        front = back - ans_size
        # Set values in answer
        answer = {}
        answer['name'] = name
        answer['type'] = atype
        answer['class'] = aclass
        answer['ttl'] = ttl
        answer['data_length'] = data_length
        answer['address'] = address
        answer['ip_address'] = ip_address
        # update answers
        self.answers.append(answer)

  
  def getHeader(self):
    return self.header
  
  def getQuery(self):
    return self.query
  
  def getAnswers(self):
    return self.answers
  
  def getIPResults(self):
    return list(map((lambda ans : ans['ip_address']), self.answers))