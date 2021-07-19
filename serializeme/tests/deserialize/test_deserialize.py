from serializeme import IPv4, PREFIX_LENGTH, HOST, Deserialize


def test_IPV4():
    pack = Deserialize(b'\x32\xff\xff\xff\xff', {
        'id': '1B',
        "dest": ('4B', IPv4)
    })
    assert pack.get_value('id') == 50
    assert pack.get_value('dest') == '255.255.255.255'


def test_host_addr():
    pack = Deserialize(b'\x05\x01\x00\x03\x0ewww.google.com\x00P', {
        "VER": "1B",
        "CMD": "1B",
        "RSV": "1B",
        "ATYP": "1B",
        "DADDR": (PREFIX_LENGTH, HOST),
        "DPORT": "2B",
    })
    assert pack.get_value('DADDR') == 'www.google.com'
    assert pack.get_value('DPORT') == 80


def test_prefix_length():
    rsp = b'\x01\x06cs158b\x08Pa55word'

    pck = Deserialize(rsp, {
        "VER": "1B",
        "ID": PREFIX_LENGTH,
        "PW": PREFIX_LENGTH
    })

    assert pck.get_value("VER") == 1
    assert pck.get_value("ID") == 'cs158b'
    assert pck.get_value("PW") == 'Pa55word'


def test_variables():
    rsp = b'\x01\x03\x00\x01\x02'
    vals = [0, 1, 2]
    pck = Deserialize(rsp, {
        "VER": "1B",
        "NAUTHS": ('1B', "", "AUTHS"),
        "AUTHS": {
            'val': '1B'
        }
    })

    assert pck.get_value("NAUTHS") == 3
    for f, i in pck.get_value('AUTHS'):
        assert f.get_value == vals[i]

# pck = Deserialize(b'\x41\x33', {
#     "!!2B": {'b0': '',
#              'b1': '3b',
#              'b2': '4b',
#              'b3': '4b',
#              'b4': '4b',
#              }
# })

# print(pck.get_value("b0"))
# print(pck.get_value("b1"))
# print(pck.get_value("b2"))
# print(pck.get_value("b3"))
# print(pck.get_value("b4"))

# # DNS example
# dns_request = {
#     "ID": "2B",
#     "!!2B": {
#         'QR': '1b',
#         'OPCODE': '4b',
#         'AA': '1b',
#         'TC': '1b',
#         'RD': '1b',
#         'RA': '1b',
#         "Z": "3b",
#         "RCODE": "4b",
#     },
#     "QDCOUNT": ("2B", "", "QUERIES"),
#     "ANCOUNT": "2B",
#     "NSCOUNT": "2B",
#     "ARCOUNT": "2B",
#     "QUERIES": {
#         "QNAME": PREFIX_LEN_NULL_TERM,
#         "QTYPE": "2B",
#         "QCLASS": "2B"
#     }
# }

# pck = Deserialize(b'\xccD\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x06google\x03com\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08\xd9\xd7\xa3\xbf\xe7\xb3\xae\xb9', dns_request)
# print(pck.get_value('QUERIES')[0][0].value)
# pck = Deserialize(b'\x10\xf0\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x011\x011\x0216\x03172\x07in-addr\x04arpa\x00\x00\x0c\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08\xdc\x10\xd7\xca"\xf7\xc4\xb7', dns_request)
# print(pck.get_value('QUERIES')[0][0].value)
