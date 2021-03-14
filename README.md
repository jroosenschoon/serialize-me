# Serialize
___
##Table of Content
* [Introduction](#Introduction)
* [Setup](#setup)
* [Basic Example](#Basic-Example)
* [Packet Formatting](#Packet-formattig)
* [Package Structure](#package-structure)

##Introduction
___


###Overview
___

| Component      | Description     | 
| :------------- | :----------: | 
|  [serializeme]("https://github.com/jroosenschoon/serialize-me/tree/main/serializeme") | serializeme is a library meant for building network packets from user-specified fields  | 
| [field.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/field.py") | Create fields to add to packets | 
| [serialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/serialize.py") | Generate packets that can be sent over the network |
| [deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/serializeme/deserialize.py") | Extract information from packets received over the network |

##Setup
___
Currently, `serializeme` supports releases of Python 3. Python 2 is not supported (and not recommended).
To install the current release of `serializeme`, simply use `pip`:

``` pip install serializeme```

##Basic Example
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

##Packet Formatting
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
| `()`           | Field with 1 bit of value 0 | 

For [deserialize.py]("https://github.com/jroosenschoon/serialize-me/blob/main/deserializeme/serialize.py"), the following formats are currently supported:

| Format         | Description     |  Example |
| :------------- | :----------: | :----:      |
| `()`           | Field with 1 bit of value 0 | 




##Package Structure
___




# Utilities:
## Field.py
### What it does?
It is a python program that represents and initializes a field in one of the packets.

### How it works?

The Field.py initializes the name, the size and the value of each field.
  
It consists of two function which will be called based on the specified size of the field:
  
to_binary() is used to convert the value of a given field into binary

to_hex() is used to convert the value of a given field into hex
  
  
## Serialize.py
### What it does?
It builds the actual packet using the dictionary data specified by the users and creates a list of fields.
 
### How it works?
It initializes the data as a dictionary, which contains the fields specified by the users.

It consists of two main functions:

packetize() takes in all the fields that were specifized through the dictionary variable called data and then converts it into a byte array.

Another important function in the serialize.py is get_field() which either find and return a specified field that matches one of the elements in the fields array or return none if nothing is found.

## SerializeEX.py  
  
### What it does?
It creates a variable called dnc_packet where the dictionary of packet is being sent to the Serialize.py 

### How it works?
As shown below the data is represented in a dictionary format and the data is passed as a parameter to the Serialize function present in the serialize.py program.


