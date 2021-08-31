TYPE_LENGTH = 2
LENGTH_LENGTH = 1
CRC_LENGTH = 4
ENDIAN = "little"

PREAMBLE = b'\xaa\x44\x12'

# MESSAGE_FIELDS = [
# 	("msgtype", "2s"),
# 	("payload_length", "B"),
# 	("payload", "24s"), #TODO - this won't be same for all message types. so should check payload_length first
# 	("crc", "i")
# ]

	#counter: 4 byte unsigned int
	#system clock seconds: 2 byte unsigned int
	#system clock milliseconds: 2 byte unsigned int
	#system clock microseconds: 2 byte unsigned int
	#accelerometer x/y/z: 3x 2 byte signed int 
	#angular rate x/y/z: 3x 2 byte signed int
	#temperature:	2 byte signed int

RS_PAYLOAD_LEN = 24

RS_PAYLOAD_FIELDS = [
	("counter", "I"),
	("seconds", "H"),
	("milliseconds", "H"),
	("microseconds", "H"),
	("accel_x", "h"),
	("accel_y", "h"),
	("accel_z", "h"),
	("rate_x", "h"),
	("rate_y", "h"),
	("rate_z", "h"),
	("temperature", "h")
]

FULL_SS_MESSAGE_FIELDS = [
    ("msgtype", "2s"),
    ("payload_length", "B"),
    ("payload", "42s"),
    ("crc", "i")
]

SS_PAYLOAD_LEN = 42

SS_PAYLOAD_FIELDS = [
    ("counter", "I"),
    ("seconds", "H"),
    ("milliseconds", "H"),
    ("microseconds", "H"),
    ("accel_x", "f"),
    ("accel_y", "f"),
    ("accel_z", "f"),
    ("rate_x", "f"),
    ("rate_y", "f"),
    ("rate_z", "f"),
    ("rate_fog", "f"),
    ("temperature", "f")
]
