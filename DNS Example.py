# Serialize package:
#     dns - RRQuestion(), RRResponse(), etc.
#     transport - UDP(), TCP()
#     ...
#     Packet - general packet building (with dict?)
#          packet = Packet(dict)

rr = dns.ResourceRecordQuestion()


# Attributes: id, opcode, trunc, domain, etc...
# rr.set_id(16) #rr.id = 16
#
# rr.set_qr(1) # Default = 0
#
# rr.set_opcode(1) # Default = 0
#
# rr.set_aa(0) # default
# Etc.

rr.qname("google.com")

socket.send(rr.packetize())
# Throws exception if something is not set properly.

print(rr) # Or just print(rr) # Returns:
# Resource Record
# id: 16
# qr: 1 (query)
# opcode: 4 (...)
# ...


response = dns.receive(data)
response.errorcode --> 0
response.data      --> ip
...
