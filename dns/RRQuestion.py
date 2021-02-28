from header import Header
import struct
import socket

class RRQuestion:
    def __init__(self, queries, qtype=1, qclass=1, id=-1, qr=0, opcode=0,
                 aa=0, tc=0, rd=1, ra=0, rcode=0,
                 qdcount=1, ancount=0, nscount=0, arcount=0):
        # TODO Check for errors. Some ideas:
        #   - some value too big or negative
        #   - z is not 0.
        #   - etc.
        if qdcount_ not in [0, 1]:
            raise Exception("qdcount must be 0 for nonquestions or 1 for a question.\n value was {}".format(qdcount))




        self.hdr = Header(id, qr=qr, opcode=opcode,
                     aa=aa, tc=tc, rd=rd, ra=ra, rcode=rcode,
                     qdcount=qdcount, ancount=ancount, nscount=nscount, arcount=arcount)

        self.queries = queries
        self.qtype   = qtype
        self.qclass  = qclass


    def packetize(self):
        q = b''
        parts = self.queries.split(".")
        for part in parts:
            q += bytes([len(part)]) + part.encode()
        q += b'\0'
        return self.hdr.packetize() + q + struct.pack('!HH', self.qtype, self.qclass)

    def __str__(self):
        # TODO Add verbose option
        s = str(self.hdr)
        s += "Queries\n"
        s += "    " + self.queries + "\n"
        s += "QTYPE : " + str(self.qtype) + "\n"
        s += "QCLASS: " + str(self.qclass) + "\n"
        return s

# UDP IPv4 socket.
sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Establish "connection" to specified ip with port 53 (DNS port)
sd.connect(('8.8.8.8', 53))

r = RRQuestion("google.com")

print(r)

sd.send(r.packetize())
