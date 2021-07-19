from serializeme import IPv4, Deserialize
from serializeme import Field


def test_get_field():  # sourcery skip: extract-duplicate-method
    pack = Deserialize(b'\x32\xff\xff\xff\xff', {
        'id': '1B',
        "dest": ('4B', IPv4)
    })
    f = Field('id', 1, 50)

    assert pack.get_field('id').name == f.name
    assert pack.get_field('id').size == f.size
    assert pack.get_field('id').value == f.value

    f = Field('dest', 16, '255.255.255.255')

    assert pack.get_field('dest').name == f.name
    assert pack.get_field('dest').size == f.size
    assert pack.get_field('dest').value == f.value
