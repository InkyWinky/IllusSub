from enum import Enum, IntEnum


# The below class is the Enums for MAV_RESULTS in the fields of "COMMAND_ACK" (https://mavlink.io/en/messages/common.html#COMMAND_ACK)
class CommandResults(IntEnum):
    MAV_RESULT_ACCEPTED = 0
    MAV_RESULT_TEMPORARILY_REJECTED = 1
    MAV_RESULT_DENIED = 2
    MAV_RESULT_UNSUPPORTED = 3
    MAV_RESULT_FAILED = 4
    MAV_RESULT_IN_PROGRESS = 5
    MAV_RESULT_CANCELLED = 6
    MAV_RESULT_COMMAND_LONG_ONLY = 7
    MAV_RESULT_COMMAND_INT_ONLY = 8
    MAV_RESULT_COMMAND_UNSUPPORTED_MAV_FRAME = 9


class MUASCommands(IntEnum):
    WADJET = 975
    LIFELINE = 976


class WadjetCommands(IntEnum):
    NEUTRAL_MODE = 0
    TRACK_GPS_MODE = 1
    TRACK_TARGET_MODE = 2
    RESET_POSITION = 3


class LifelineCommands(IntEnum):
    DROP_PAYLOAD = 0
    SMERF = 1
    NERF = 2


class MUASComponentID(IntEnum):
    WADJET = 169
    VISION = 170
    LIFELINE = 171
    MISSION_MANAGEMENT = 172


class LifelineCommandResults(IntEnum): 
    DOOR_OPENING = 310
    DOOR_OPENING_SUCCESS = 311
    DOOR_OPENING_FAILED = 312

    DOOR_CLOSING = 510
    DOOR_CLOSING_SUCCESS = 511
    DOOR_CLOSING_FAILED = 512
    

class LifelineState(Enum):
    # defining state constants
    LOADING = 100
    IDLE = 200
    LOWERING = 300
    RELEASING = 400
    RAISING = 500
    EMERGENCY = 900
    NERF = 800
  

