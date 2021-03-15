# Serialize
___
## Table of Content
* [Introduction](#Introduction)
* [Setup](#setup)
* [Basic Example](#Basic-Example)
* [Packet Formatting](#Packet-formatting)
* [Documentation](#Documentation)
* [Package Structure](#package-structure)

## Introduction
___


### Overview
___

| Component      | Description     | 
| :------------- | :----------: | 
|  [serializeme]("https://github.com/jroosenschoon/serialize-me/tree/main/serializeme") | serializeme is a library meant for building network packets from user-specified fields  | 
| [field.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/field.py") | Create fields to add to packets | 
| [serialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/serialize.py") | Generate packets that can be sent over the network |
| [deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/deserialize.py") | Extract information from packets received over the network |

## Setup
___
Currently, `serializeme` supports releases of Python 3. Python 2 is not supported (and not recommended).
To install the current release of `serializeme`, simply use `pip`:

``` pip install serializeme```

## Basic Example
Using  `serializeme` to send data.
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
___
`serializme` aims to be as flexible as possible allowing the user to enter the desired format as they see fit. As such, there is a wide variety of ways to specify formats.
To create a packet format, create a python Dictionary of the following form:
```python
packet_format = {
    "field_name": <field_Structure>
}
```
Where `<field_Structure>` looks like the following:

For [serialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/serialize.py"), the following formats are currently supported:

| Format         | Description     |  Example |
| :------------- | :----------: | :----:      |
| `()`           | Field with 1 bit of value 0  | `()` creates `0`   |
| `4`            | Field with 4 bits of value 0 | `4` creates `0000` |
| `"5b"`         | Field with 5 bits of value 0 | `"5b"` creates `00000` |
| `"1B"`         | Field with 1 byte of value 0 | `"1B"` creates `00000000` |
| `(4, 3)`       | Field with 4 bits of value 3 | `(4, 3)` creates `0011` |
| `("3b", 2)`    | Field with 3 bits of value 2 | `("3b", 2)` creates `010` |
| `("2B", 255)`  | Field with 1 bytes of value 255 | `("2B", 255)` creates `0000000011111111` |
|  `(KEYWORD, data)` | Create a variable-length field terminating by a specified way. Currently, there are three ways (see below) |  `(serialize.PREFIX_LEN_NULL_TERM, ("google", "com"))` creates `0x06google0x03com0x00`

Currently `serializme` supports three ways to handle variable-length fields:
* `serialize.PREFIX_LEN_NULL_TERM` : Creates a field that will automatically append the length of each element, then the actual element, and then after the at the end, a byte of zeros
* `serialize.NULL_TERMINATE` : Creates a field that will automatically add a byte of zeros at the end
* `serialize.PREFIX_LENGTH` : Creates a field that will automatically append the length of each element, then the actual element.


For [deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/deserialize.py"), the following formats are currently supported:

| Format                                           |                                                 Description                                                  |                                              Example                                              |
| :----------------------------------------------- | :----------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------: |
| `(size, format, variable)`                       |                                               parameter order                                                |                                                NA                                                 |
| `(1B)`                                           |                               1 bytes of data, default formatting, no variable                               |                                     creates a field of 1 byte                                     |
| `(serializeme.NULL_TERMINATE, serializeme.HOST)` |                 null terminating length (bytes end in \x00), format to hostname, no variable                 | creates a variable length field depending on finding `0x00`. formats the result to a hostname format |
| `(2b, '', 'ANSWERS')`                            | 2 bytes of data , default formatting, variable ANSWERS (the result of this field will cycle through ANSWERS) |                                           see next line                                           |
| `ANSWERS: { name: (2B, serializeme.HOST) }`      |   will _repeat_ according to ANWSERS value and get field name for 2 bytes of data and format as a hostname   |                   `acnt: (2b, '','ANSWERS'), ... ANSWERS: { dns answers data}`                    |
## Documentation
___


## Package Structure
___
## Utilities:
### Field.py
#### What it does?
It is a python program that represents and initializes a field in one of the packets.

#### How it works?

The Field.py initializes the name, the size and the value of each field.
  
It consists of two function which will be called based on the specified size of the field:
  
to_binary() is used to convert the value of a given field into binary

to_hex() is used to convert the value of a given field into hex
  
  
### Serialize.py
#### What it does?
It builds the actual packet using the dictionary data specified by the users and creates a list of fields.
 
#### How it works?
It initializes the data as a dictionary, which contains the fields specified by the users.

It consists of two main functions:

packetize() takes in all the fields that were specifized through the dictionary variable called data and then converts it into a byte array.

Another important function in the serialize.py is get_field() which either find and return a specified field that matches one of the elements in the fields array or return none if nothing is found.

### SerializeEX.py  
  
#### What it does?
It creates a variable called dnc_packet where the dictionary of packet is being sent to the Serialize.py 

#### How it works?
As shown below the data is represented in a dictionary format and the data is passed as a parameter to the Serialize function present in the serialize.py program.


