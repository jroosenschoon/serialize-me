# Serialize

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


