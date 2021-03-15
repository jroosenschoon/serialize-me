# Serialize

---

## Table of Content

- [Introduction](#Introduction)
- [Setup](#setup)
- [Basic Example](#Basic-Example)
- [Packet Formatting](#Packet-formatting)
- [Documentation](#Documentation)
- [Utilities](#Utilities)

## Introduction

---

The goal of `serializeme` is to provide a streamlined way to create networking packets and to extract the fields from networking packets. There are two primary classes:

- `serialize.py` which will encode decimal values in a specified size into a byte array
- `deserialize.py` which will decode a byte string given the way the bytes are laid out.

### Overview

---

`serializeme` consists of the following components:
| Component | Description |
| :------------- | :----------: |
| [serializeme]("https://github.com/jroosenschoon/serialize-me/tree/main/serializeme") | serializeme is a library meant for building network packets from user-specified fields |
| [field.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/field.py") | Create fields to add to packets |
| [serialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/serialize.py") | Generate packets that can be sent over the network |
| [deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/deserialize.py") | Extract information from packets received over the network |

## Setup

---

Currently, `serializeme` supports releases of Python 3. Python 2 is not supported (and not recommended).
To install the current release of `serializeme`, simply use `pip`:

` pip install serializeme`

## Basic Example

Using `serializeme` to send data.

```python
import serializeme
import socket


dns_packet = serializeme.Serialize({<PACKET FORMAT>})

# Connect to Google's namespace server
sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))

sd.send(dns_packet.packetize())
```

Using `serializeme` to receive and extract data.

```python
import serializeme
import socket

# Connect to Google's namespace server
sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sd.connect(('8.8.8.8', 53))

rsp = sd.recv(1024)
pack = serializeme.Deserialize(rsp, {<PACKET FORMAT>})
```

## Packet Formatting

---

`serializme` aims to be as flexible as possible allowing the user to enter the desired format as they see fit. As such, there is a wide variety of ways to specify formats.
To create a packet format, create a python Dictionary of the following form:

```python
packet_format = {
    "field_name": <field_Structure>
}
```

Where `<field_Structure>` looks like the following:

For [serialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/serialize.py"), the following formats are currently supported:

| Format            |                                                Description                                                 |                                        Example                                        |
| :---------------- | :--------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------: |
| `()`              |                                        Field with 1 bit of value 0                                         |                                   `()` creates `0`                                    |
| `4`               |                                        Field with 4 bits of value 0                                        |                                  `4` creates `0000`                                   |
| `"5b"`            |                                        Field with 5 bits of value 0                                        |                                `"5b"` creates `00000`                                 |
| `"1B"`            |                                        Field with 1 byte of value 0                                        |                               `"1B"` creates `00000000`                               |
| `(4, 3)`          |                                        Field with 4 bits of value 3                                        |                                `(4, 3)` creates `0011`                                |
| `("3b", 2)`       |                                        Field with 3 bits of value 2                                        |                               `("3b", 2)` creates `010`                               |
| `("2B", 255)`     |                                      Field with 1 bytes of value 255                                       |                       `("2B", 255)` creates `0000000011111111`                        |
| `(KEYWORD, data)` | Create a variable-length field terminating by a specified way. Currently, there are three ways (see below) | `(serialize.PREFIX_LEN_NULL_TERM, ("google", "com"))` creates `0x06google0x03com0x00` |

Currently `serializme` supports three ways to handle variable-length fields:

- `serialize.PREFIX_LEN_NULL_TERM` : Creates a field that will automatically append the length of each element, then the actual element, and then after the at the end, a byte of zeros
- `serialize.NULL_TERMINATE` : Creates a field that will automatically add a byte of zeros at the end
- `serialize.PREFIX_LENGTH` : Creates a field that will automatically append the length of each element, then the actual element.

For [deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/deserialize.py"), the following formats are currently supported:

| Format                                           |                                                 Description                                                  |                                               Example                                                |
| :----------------------------------------------- | :----------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------: |
| `(size, format, variable)`                       |                                               parameter order                                                |                                                  NA                                                  |
| `(1B)`                                           |                               1 bytes of data, default formatting, no variable                               |                                      creates a field of 1 byte                                       |
| `(serializeme.NULL_TERMINATE, serializeme.HOST)` |                 null terminating length (bytes end in \x00), format to hostname, no variable                 | creates a variable length field depending on finding `0x00`. formats the result to a hostname format |
| `(2b, '', 'ANSWERS')`                            | 2 bytes of data , default formatting, variable ANSWERS (the result of this field will cycle through ANSWERS) |                                            see next line                                             |
| `ANSWERS: { name: (2B, serializeme.HOST) }`      |   will _repeat_ according to ANWSERS value and get field name for 2 bytes of data and format as a hostname   |                     `acnt: (2b, '','ANSWERS'), ... ANSWERS: { dns answers data}`                     |

## Documentation

---

### Serialize

Create a byte string from a dictionary of `"name": data` pairs representing fields in a packet.
[serialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/serialize.py")

```python
serializeme.Serialize(data)
```

---

### Parameters

- **data**: **Dictionary**, the dictionary containing all of the fields in the format `"name": <field_Structure>` where `<field_Structure>` is one of the following:
  - `()`: Creates a field with 1 bit of value 0.
  - `N`: Creates a field with `N` bits of value 0. Note: `N` is a nonnegative number.
  - `"Nb"`: Creates a field with `N` bits of value 0. Note: `N` is a nonnegative number.
  - `"NB"`: Creates a field with `N` bytes of value 0. Note: `N` is a nonnegative number.
  - `(N, M)`: Creates a field with `N` bits of value `M`. If `M` cannot be stored in `N` bits, an exception is thrown.
  - `("Nb", M)`: Creates a field with `N` bits of value `M`. If `M` cannot be stored in `N` bits, an exception is thrown.
  - `("NB", M)`: Creates a field with `N` bytes of value `M`. If `M` cannot be stored in `N` bytes, an exception is thrown.
  - `(KEYWORD, data)`: Creates a variable-length field that is ended by one of three possibilities, denoted by the `KEYWORD`. Possible values are:
    - `serialize.PREFIX_LEN_NULL_TERM`: Creates a field that will automatically append the length of each element, then the actual element, and then after the at the end, a byte of zeros
    - `serialize.NULL_TERMINATE`: Creates a field that will automatically add a byte of zeros at the end
    - `serialize.PREFIX_LENGTH`: Creates a field that will automatically append the length of each element, then the actual element.

### Methods

---

| Method             |                              Description                              |                  Parameters                  |       Return        |
| :----------------- | :-------------------------------------------------------------------: | :------------------------------------------: | :-----------------: |
| `packetize()`      | Convert all of the fields of the Serialize object into a byte string. |                      NA                      |        bytes        |
| `get_field(field)` |     Return the specified field if found. Return `None` otherwise.     | `field`: The name of the field to search for | `serializeme.Field` |

### Deserialize

Deconstruct a packet given a prefined structure
[deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/deserialize.py")

```python
serializeme.Deserialize(rsp, data)
```

---

### Parameters

- **rsp**: **Packet**, pass in a packet to be deconstructed
- **data**: **Dictionary**, the dictionary containing all of the fields in the format

### Methods

---

| Method                  |                Description                 |                    Parameters                     |       Return        |
| :---------------------- | :----------------------------------------: | :-----------------------------------------------: | :-----------------: |
| `get_field(field_name)` | returns the given field for the field_name | a field name that is part of the data constructor | `serializeme.Field` |

### Field

Create a basic field object that is used in `serializeme.Serialize` and `serializeme.Deserialize`
[field.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/field.py")

```python
serializeme.Field(name, size, value)
```

---

### Parameters

- **name**: **str**, The name of the field.
- **size**: **int** or **str**, The size, in bits of the field, or a string denoting a certain type of variable-length field. Possible values include:
  _ `serialize.PREFIX_LEN_NULL_TERM`: Creates a field that will automatically append the length of each element, then the actual element, and then after the at the end, a byte of zeros
  _ `serialize.NULL_TERMINATE`: Creates a field that will automatically add a byte of zeros at the end \* `serialize.PREFIX_LENGTH`: Creates a field that will automatically append the length of each element, then the actual element.
- **value**: **int**, The value of the field, in decimal.

---

| Method        |                                 Description                                 | Parameters | Return |
| :------------ | :-------------------------------------------------------------------------: | :--------: | :----: |
| `to_binary()` | Return a binary string of the field. Currently only works for static sizes. |     NA     | `str`  |
| `to_hex()`    |  Return a hex string of the field. Currently only works for static sizes.   |     NA     | `str`  |

## Utilities

---

### Field.py

#### What it does?

It is a program that initializes a field in one of the packets.

#### How it works?

The `field.py` initializes the name, the size and the value of each field.

It consists of two function which will be called based on the specified size of the field. The `to_binary()` function is used to convert value of a given field to binary. The `to_hex()` function is used to convert the value of a given field into hex.

### Serialize.py

#### What it does?

It builds the actual packet using the dictionary data specified by the users and creates a list of fields.

#### How it works?

It initializes the data as a dictionary, which contains the fields specified by the users.

The `get_field()` function either finds and returns a specified field that matches one of the elements in the fields array or return none if nothing is found. Then it consists of two functions that will be to create list of fields. The `packetize()` function takes in all the fields that were specifized through the dictionary variable called data and then converts it into a byte array.

### deserialize.py

#### What it does?

This function deserializes gets the information of packet and data from the `test_main.py` program and itterates through those values to display them in the correct and specificied format, like IPv4, IPv6 or HOST.

#### How it works?

The init function initializes the packet, data, fields array, variables array and also calls a private function `readPacket()`.

The `readPacket()` function iterates through all the parameters passed by `test_main.py` program. If it finds a dictionary parameter, then function understands that the value is a variable and that it should be itterated using a for loop. If it is not a dictionary, we do not use any loop to read it.

`read_bit_string()` reads the bit string value, like 1B, in the given in the dictionary data parameter and returns a the integer size and the format of bit string. If an empty bit string value is passed then the function returns 1 as the size for a bit with no formatting and no variable.

The `handle_custom_formatting()` is a function that decides whether the bits are going to be formatted in IPv4, IPv6 or HOST.

The `get_field()` function is used to save all an array of data, like an array of answers, as a field.

### test_main.py

#### What it does?

It creates a variable called dnc_packet where the dictionary of packet is being sent to the `serialize.py`. It also passes a packet and a dictionary data to the `deserialize.py` file.

#### How it works?

In the program we have a variable `dns_packet` to test the serialize.py program. The data is represented in a dictionary format and the data is passed as a parameter to the Serialize function present in the serialize.py program.

There could different formats of the dictionary. One format could be where the user specifies the size of the field and the value of the field, like `"name": (size, value)`. The second format could be where the user only specifies the size and the value defaults to 0, i.e., `"name": (size)`. The third format would be that a user can choose to neither size nor value, i.e., `"name": ()`, and the default values for size becomes 1 bit and value becomes 0.

A size can be a number that defaults to the number of bits or it could be a string like "2b" or "2B".

---

We create another variable named pack and test the `deserialize.py` function by assigning `pack` the value returned by the deserialize function with a packet and a formatting dictionary as its two parameters.

Let us look at a detailed description of the second parameter (formatting dictionary):
The dictionary formatting is represented in the form of a name field containing three values i.e., number of bytes, formatting string and variable. For clarification, an example of name field with the 3 values would be `'qcnt': ('1B','','Questions')`. The formatting string is implemented to give users different static options like a HOST domain or an IPv4. A variable is used as the third value of the name field so that the user will have the option to pass multiple questions to a DNS and/or get multiple answers for a value without any issues.
