import struct

class Deserialize: 
  def __init__(self, packet):
    self.packet = packet
    self.header = {}
    self.query = {}
    self.answers = []
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
    # print(struct.calcsize('!QHH'))
    query = self.packet[13:32]
    print(query)
    # self.query['qname'] = query[0]
    # self.query['qtype'] = query[1]
    # self.query['qclass'] = query[2]

    # Handle the correct query type (IPv4 / IPv6)
    if self.header['acnt'] > 0:
      back = len(self.packet)
      front = back - 16
      for x in range(0, self.header['acnt']):
        (name, atype, aclass,ttl,data_length, address) = struct.unpack('!HHHIHI',self.packet[front:back])
        s = str(hex(address))[2:]
        # format address into ip address
        ip_address = ('.'.join(str(int(i, 16)) for i in ([s[i:i+2] for i in range(0, len(s), 2)])))
        # loop for multiple results
        back = front
        front = back - 16
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
