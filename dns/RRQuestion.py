from header import Header
import struct
import socket

class RRQuestion:
    def __init__(self, queries, qtype=1, qclass=1, id_=-1, qr_=0, opcode_=0,
                 aa_=0, tc_=0, rd_=1, ra_=0, rcode_=0,
                 qdcount_=1, ancount_=0, nscount_=0, arcount_=0):

        self.hdr = Header(id_, qr=qr_, opcode=opcode_,
                     aa=aa_, tc=tc_, rd=rd_, ra=ra_, rcode=rcode_,
                     qdcount=qdcount_, ancount=ancount_, nscount=nscount_, arcount=arcount_)

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


# UDP IPv4 socket.
sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Establish "connection" to specified ip with port 53 (DNS port)
sd.connect(('8.8.8.8', 53))

r = RRQuestion("google.com")

print(r.hdr)


# sd.send(r.packetize())
