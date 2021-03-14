from .serialize import Serialize
from .deserialize import Deserialize

from .field import Field


from .serialize import NULL_TERMINATE, PREFIX_LENGTH, PREFIX_LEN_NULL_TERM
from .deserialize import HOST,  IPv4, IPv6, NULL_TERMINATE

# if PREFIX_LENGTH or PREFIX_LEN_NULL_TERM:
#     data_len = struct.unpack("!H", data[:1])[0]
#     ip =
