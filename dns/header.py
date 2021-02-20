import struct
import socket
from random import randint
class Header:
    def __init__(self, id=-1, qr=0, opcode=0,
                 aa=0, tc=0, rd=1, ra=0, rcode=0,
                 qdcount=1, ancount=0, nscount=0, arcount=0):
        if id < 0:
            self.id = randint(1, 10000)
        else:
            self.id = id

        self.qr      = qr
        self.opcode  = opcode
        self.tc      = tc
        self.aa      = aa
        self.rd      = rd
        self.ra      = ra
        self.z       = 0
        self.rcode   = rcode
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = nscount
        self.arcount = arcount


    def packetize(self):
        # Check for errors. Some ideas:
        #   - some value too big or negative
        #   - z is not 0.
        #   - etc.
        row2 = "{:b}{:04b}{:b}{:b}{:b}{:b}{:03b}{:04b}".format(self.qr, self.opcode,
                        self.tc, self.aa, self.rd, self.ra, self.z, self.rcode)

        hdr = struct.pack('!HHHHHH', self.id, int(row2, 2), self.qdcount, self.ancount, self.nscount, self.arcount)

        return hdr


    def __str__(self):
        s = " DNS Header\n\n"
        s += "    FIELD     DEC            BIN             HEX\n"
        s += "  " + "-"*47 + "\n"
        s += "   ID        {:^6s}   {:016b}      {:x}\n".format(str(self.id), self.id, self.id)
        s += "   QR        {:^6s}   {:b}      {:>16x}\n".format(str(self.qr), self.qr, self.qr)
        s += "   OPCODE    {:^6s}   {:04b}      {:>13x}\n".format(str(self.opcode), self.opcode, self.opcode)
        s += "   TC        {:^6s}   {:b}      {:>16x}\n".format(str(self.tc), self.tc, self.tc)
        s += "   AA        {:^6s}   {:b}      {:>16x}\n".format(str(self.aa), self.aa, self.aa)
        s += "   RD        {:^6s}   {:b}      {:>16x}\n".format(str(self.rd), self.rd, self.rd)
        s += "   Z         {:^6s}   {:03b}      {:>14x}\n".format(str(self.z), self.z, self.z)
        s += "   RCODE     {:^6s}   {:04b}      {:>13x}\n".format(str(self.rcode), self.rcode, self.rcode)
        s += "   QDCOUNT   {:^6s}   {:016b}      {:x}\n".format(str(self.qdcount), self.qdcount, self.qdcount)
        s += "   ANCOUNT   {:^6s}   {:016b}      {:x}\n".format(str(self.ancount), self.ancount, self.ancount)
        s += "   NSCOUNT   {:^6s}   {:016b}      {:x}\n".format(str(self.nscount), self.nscount, self.nscount)
        s += "   ARCOUNT   {:^6s}   {:016b}      {:x}\n".format(str(self.arcount), self.arcount, self.arcount)
        return s
