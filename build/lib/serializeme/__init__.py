"""
The serializeme module allow users to encode and decode network packets with ease.
"""

from .serialize import Serialize
from .deserialize import Deserialize

from .field import Field

from .serialize import NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM, IPv4
from .deserialize import HOST,  IPv4, IPv6, NULL_TERMINATE
