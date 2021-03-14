from serialize import Serialize
from deserialize import Deserialize


def to_packet(data):
    return Serialize(data)


def from_packet(rsp, data):
    return Deserialize(rsp, data)

