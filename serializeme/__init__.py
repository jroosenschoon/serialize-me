"""
The serializeme module allow users to encode and decode network packets with ease.
"""

NULL_TERMINATE = "null_terminate"
PREFIX_LENGTH = "prefix_length"
PREFIX_LEN_NULL_TERM = "prefix_len_null_term"
IPV4 = "ipv4"
HOST = "host"

SPECIAL_FIELD_TYPES = [
    NULL_TERMINATE,
    PREFIX_LENGTH,
    PREFIX_LEN_NULL_TERM,
    IPV4,
    HOST
]
