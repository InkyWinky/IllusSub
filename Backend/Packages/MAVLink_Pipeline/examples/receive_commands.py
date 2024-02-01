# This file receives messages published by publish.py and any messages from the SITL environment.

from CubeConnection import CubeConnection
import time

# connection_string is the string used to define the connection to the network. The current connection string here is the string required to connect to SITL simulation
# environment.
# Link to connection string examples: https://mavlink.io/zh/mavgen_python/#connection_string
connection_string = "tcp:127.0.0.1:5762" # Port 5762 is serial port 1 on the SITL simulated cube.

# Set the source mavlink system as 1 (This will always be the case for us, unless we plan on having two albatrosses running on the same network)
cube_connection = CubeConnection(connection_string)


MAVLINK_COMMAND_FILTER = ("COMMAND_INT", "COMMAND_INT.command==999", "param1")
# Setting our filters which are the message types we want to receive as obtained from here: https://mavlink.io/en/messages/common.html
filters = ["STATUSTEXT", "DEBUG_VECT"]

while True:
    # Pull the next message. This is a BLOCKING operation by default, that is, it waits until it receives ONE of the message specified then returns the message here,
    # specify tag with 'blocking=False'. If this is a time sensitive task, it is best offload this into a separate thread.

    msg = cube_connection.next_message(filters=MAVLINK_COMMAND_FILTER[0], conditions="True", blocking=True)

    # Checking if msg is of valid type
    mode = msg.param1 if msg.get_type() == "COMMAND_INT" else 0
    print(msg)
    print(mode)
