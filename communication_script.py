"""
Mission Planner Communication Script
Creates a communication link between the Backend Server and Mission Planner.
Utilises MavLink and is run as a Mission Planner Script.

Script Usage
From Mission Planner Home, navigate to "Simulation" -> "Plane" -> "Stable".
On the left side, navigate to "Scripts" -> "Select Script" -> "Upload" ->
 -> "Run Script"
"""

print("Importing Dependencies...")
# import sys
# sys.path.append(r"c:/python27/lib")
import socket
import json
import clr
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink")
import MAVLink
print("Starting Script...")


class MissionManager:
    """The Mission Manager Class interfaces with Mission Planner/MAVLink to dynamically change waypoints during a mission.
    """
    def __init__(self, sync=True, connect=True, chunk_size=1024, port=7766):
        """Constructor

        Args:
            sync (bool, optional): decides if we get the waypoints from Mission Planner on startup. Defaults to True.
            connect (bool, optional): decides if the connection to the backend server is opened on startup. Defaults to True
            chunk_size (int, optional): Defines the packet size of each TCP packet. Defaults to 1024
            port (int, optional): The ephemeral port number that the connection to the backend server will run on. 
        """
        # Attributes for Waypoint access from Mission Planner.
        self.id = int(MAVLink.MAV_CMD.WAYPOINT)  # id_mav_cmd for waypoints
        self.waypoint_count = 0  # The number of waypoints
        self.waypoints = []  # list of the waypoints

        # By default, the class will sync the waypoints from mission planner.
        if sync:
            self.sync()
        
        # Attributes for Socket connection.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The Python Socket class.
        self.connection = None  # The Socket Connection that was received
        self.addr = None  # The Address of the received Socket Connection
        self.PORT = port  # The port number that the application is running on (default 7766)
        self.chunk_size = chunk_size  # The chunk size of the data sent a received (default 1024)
        if connect:
            self.__establish_connection()  # open the connection


    def __str__(self):
        """Custom print str. Called by using 'print(MissionManager())' 

        Returns:
            string: A string that contains the lat, lng and alt of all waypoints.
        """
        if self.waypoint_count == 0:
            return "Waypoints ---> Empty"
        
        txt = "----------------------------------------------\nWaypoints\n [num]. latitude, longitude, altitude\n"
        for i in range(self.waypoint_count):
            wp = self.waypoints[i]
            txt += "[" + str(i) + "]. " + str(wp.lat) + ", " + str(wp.lng) + ", " + str(wp.alt) + "\n"
        return txt + "----------------------------------------------"
    

    def __getitem__(self, index):
        """Custom get item. Is called by using 'wp = MissionManager()[index]'.

        Args:
            index (int): The index to get the waypoint at.

        Returns:
            Locationwp: The waypoint at the specified index, or None if it does not exist.
        """
        if index < self.waypoint_count:
            return self.waypoints[index]
        return None
    

    def __setitem__(self, index, waypoint):
        """ Custom set item. Is called by using 'MissionManager()[index] = waypoint'.

        Args:
            index (int): The index to set the waypoint at.
            waypoint (Locationwp): The waypoint to be set.
        """
        if index < self.waypoint_count:
            self.waypoints[index] = waypoint
        else:
            print("ERROR: Setting Waypoint at index " + str(index) + " was out of bounds.")
    

    def sync(self):
        """Syncs all the waypoints in Mission Planner to waypoints list (overrides any previous changes if update was not called)
        """
        self.waypoint_count = MAV.getWPCount()
        self.waypoints = [MAV.getWP(index) for index in range(MAV.getWPCount())]


    def append(self, waypoint):
        """Adds a waypoint to the end of the mission/list

        Args:
            waypoint (Locationwp): The waypoint to be appended into the list.
        """
        # Update waypoint count
        self.waypoint_count += 1
        # Append to class list and Mission planner
        self.waypoints.append(waypoint)


    def insert(self, index, waypoint):
        """Inserts a waypoint at a certain index.

        Args:
            index (int): The index to insert the waypoint at.
            waypoint (Locationwp): The waypoint to be inserted into the list.
        """
        # Update waypoint count
        self.waypoint_count += 1
        # Insert into class list and Mission Planner
        self.waypoints.insert(index, waypoint)


    def remove(self, index):
        """Removes a waypoint at a certain index.

        Args:
            index (int): The index to remove the waypoint at.
        """
        self.waypoints.remove(index)


    def swap(self, index1, index2):
        """Swaps waypoints at two indices.

        Args:
            index1 (_type_): The first waypoint to swap with.
            index2 (_type_): The second waypoint to swap with.
        """
        self.waypoints[index1], self.waypoints[index2] = self.waypoints[index2], self.waypoints[index1]


    def update(self):
        """Updates Mission Planner on the modified waypoints
        """
        MAV.setWPTotal(len(self.waypoints))
        for i in range(len(self.waypoints)):
            MAV.setWP(self.waypoints[i], i, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

        MAV.setWPACK()  # Send waypoint ACK
        self.__set_home(self.waypoints[0])  # Set the home waypoint as the first waypoint
    

    def create_wp(self, lat, lng, alt):
        """Creates a waypoint

        Args:
            lat (float): The latitude in degrees.
            lng (float): longitude in degrees.
            alt (float): The altitude in meters.

        Returns:
            Locationwp: The Locationwp object which contains the lat, lng and alt. This is an object from of MAVLink/Mission Planner.
        """
        return Locationwp().Set(lat, lng, alt, self.id)
    

    def set_waypoint(self, lat, lng, alt, index):
        """Alters latitude, longitude and altitude of a waypoint via index and sets it into Mission Planner

        Args:
            lat (float): The latitude to be set in degrees.
            lng (float): longitude to be set in degrees.
            alt (float): The altitude to be set in meters.
            index (int): The index of the waypoint that will have its values changed.
        """
        wp = self[index]
        Locationwp.lat.SetValue(wp, lat)
        Locationwp.lng.SetValue(wp, lng)
        Locationwp.alt.SetValue(wp, alt)
        self[index] = wp

    
    def set_lat(self, index, value):
        """Alters latitude of a waypoint via index and sets it into Mission Planner.

        Args:
            index (int): The index of the waypoint to set the latitude.
            value (float): The latitude to be set in degrees.
        """
        wp = self[index]
        Locationwp.lat.SetValue(wp, value)
        self[index] = wp


    def set_lng(self, index, value):
        """Alters longitude of a waypoint via index and sets it into Mission Planner.

        Args:
            index (int): The index of the waypoint to set the longitude.
            value (float): The longitude to be set in degrees.
        """
        wp = self[index]
        Locationwp.lng.SetValue(wp, value)
        self[index] = wp


    def set_alt(self, index, value):
        """Alters altitude of a waypoint via index and sets it into Mission Planner.

        Args:
            index (int): The index of the waypoint to set the altitude.
            value (float): The altitude to be set in meters.
        """
        wp = self[index]
        Locationwp.alt.SetValue(wp, value)
        self[index] = wp
    

    def target_waypoint(self, index):
        """Sets the waypoint to go to in guided mode.
        Args:
            index (int): The index of the waypoint to set as target.
        """
        MAV.setGuidedModeWP(self.waypoints[index])


    def __set_home(self, waypoint):
        """Sets the home waypoint (NOTE: THIS SHOULD BE INDEX=0 IN THE WAYPOINTS LIST).
        This is a private function.

        Args:
            waypoint (Locationwp): The waypoint to be set as the home.
        """
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, waypoint.lat, waypoint.lng, waypoint.alt)
        self.waypoints[0] = waypoint
    

    def __establish_connection(self):
        """Creates an open socket connection for the backend to connect to.
        This function is private.
        """
        HOST = ""  # Open to all IP addresses. Can set to be a specific one.
        try:
            print("Waiting for a connection.")
            self.s.bind((HOST, self.PORT))
            self.s.listen(1)  # Listens for 1 connection
            self.connection, self.addr = self.s.accept()
            print("Connected by " + str(self.addr))
            while True:
                data = self.connection.recv(self.chunk_size)  # receive data in 1024 bit chunks
                print("RAW DATA RECEIVED:")
                print(data)
                self.handle_command(data)
                if data == "quit": break  # if data given is exit command
                self.connection.sendall(data)  # echo data back!
            self.close_connection()
        except Exception as e:
            # Close connection and print out error.
            self.close_connection()
            print(e)

    
    def close_connection(self):
        """Safely closes the Socket Connection.
        """
        self.s.close()
        print("Connection to " + str(self.addr) + " was lost.")
    
    def handle_command(self, data):
        """This function handles any commands sent from the backend server.

        Args:
            data (bytes): The byte stream from the socket connection that is the data of the command.
        """
        decoded_data = json.loads(data)
        command = decoded_data["command"]
        waypoints = decoded_data["waypoints"]
        # If the command is to OVERRIDE the Waypoints
        if command == Commands.OVERRIDE:
            mp_waypoints = self.convert_to_locationwp(waypoints)
            self.waypoints = mp_waypoints
            self.waypoint_count = len(mp_waypoints)
            self.update()
            print("OVERRIDE Waypoint Command Executed")
        else:
            print("Unknown Command Was Given")


    def convert_to_locationwp(self, waypoints):
        """Converts a list of dictionaries to the waypoints that mission planner uses.

        Args:
            waypoints (list[dict]): A list of dictionaries containing waypoints.

        Returns:
            list[Locationwp]: The list of Locationwp for Mission Planner to use.
        """
        n = len(waypoints)  # number of waypoints
        res = [None for _ in range(n)]  # initialize list
        for i in range(n):
            res[i] = self.create_wp(waypoints[i]["lat"], waypoints[i]["long"], waypoints[i]["alt"])
        return res


class Commands:
    """An ENUM containing all the commands that the backend server can send for execution on mission planner.
    The functions in this class will return an Action class that will be sent over the socket connection.
    """
    OVERRIDE = "OVERRIDE"


def waypoint_mavlink_test():
    """Sets the current mission to hard-coded waypoints using MAVLink functions.
    """
    id = int(MAVLink.MAV_CMD.WAYPOINT) # id_mav_cmd for waypoints
    MAV.doCommand
    home = Locationwp().Set(-37.8238872, 145.0538635, 0, id)

    takeoff = Locationwp()
    Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
    Locationwp.p1.SetValue(takeoff, 15)
    Locationwp.alt.SetValue(takeoff, 50)

    wp1 = Locationwp().Set(-37.8408347, 145.2241516, 100, id)
    wp2 = Locationwp().Set(-37.8411058, 145.2569389, 100, id)
    wp3 = Locationwp().Set(-37.8657742, 145.2680969, 100, id)
    wp4 = Locationwp().Set(-37.8818991, 145.2234650, 100, id)

    MAV.setWPTotal(6)
    MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(takeoff, 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp1, 2, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp2, 3, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp3, 4, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp4, 5, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWPACK()

    # Set Home waypoint
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, -37.8238872, 145.0538635, 0)
    


def get_ip():
    """Gets the IPs of the current device and prints them.
    """
    hostname = socket.gethostname()
    addr = socket.gethostbyname(hostname)
    print("Hostname: " + hostname + "\nAddresses: " + str(addr))


def waypoint_manager_test():
    """Adds hard-coded waypoints to the current mission using the Mission Manager Class.
    """
    mm = MissionManager(sync=False)  # Sync is set to False so that we can overwrite existing waypoints

    print("After Syncing")
    print(mm)
    home = mm.create_wp(-37.8238872, 145.0538635, 0)

    takeoff = Locationwp()
    Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
    Locationwp.p1.SetValue(takeoff, 15)
    Locationwp.alt.SetValue(takeoff, 50)

    wp1 = mm.create_wp(-37.8408347, 145.2241516, 100)
    wp2 = mm.create_wp(-37.8411058, 145.2569389, 100)
    wp3 = mm.create_wp(-37.8657742, 145.2680969, 100)
    wp4 = mm.create_wp(-37.8818991, 145.2234650, 100)

    mm.append(home)
    mm.append(takeoff)
    mm.append(wp1)
    mm.append(wp2)
    mm.append(wp3)
    mm.append(wp4)
    mm.update()
    print("After Adding")
    print(mm)

    # Sleep for 5 seconds before editing waypoint 2
    print("Sleeping for 5 seconds")
    Script.Sleep(5000)
    print("Changing waypoint 2")
    mm.set_waypoint(-37.7202198, 145.1486206, 100, 2)
    mm.update()

    #
    print("Set Guided Mode Waypoint to: wp3 (index 4)")
    mm.target_waypoint(4)
    
    # Sleep for 5 seconds before adding a new waypoint
    print("Sleeping for 5 seconds")
    Script.Sleep(5000)
    print("Adding a waypoint")
    wp5 = mm.create_wp(-37.9154926, 145.1170349, 100)
    mm.append(wp5)
    mm.update()

        
# NOTE: Script is run as a module and not as __main__.
#waypoint_mavlink_test()
#waypoint_manager_test()

get_ip()  # Print out the IPs of the device running Mission Planner.

mm = MissionManager()  # Create a mission manager class.
mm.close_connection()
print("Script Terminated!")

