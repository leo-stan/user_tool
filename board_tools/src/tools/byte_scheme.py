from ctypes import *
import os
import struct
try:  # importing from inside the package
    from config.byte_scheme_config import *
    from scheme import Scheme, Message
except ModuleNotFoundError:  # importing from outside the package
    from tools.config.byte_scheme_config import *
    from tools.scheme import Scheme, Message


# messages encoded in bytes, with preamble
class ByteScheme(Scheme):

    def read_one_message(self, connection):
        data = connection.read_until(PREAMBLE)
        if data[-len(PREAMBLE):] == PREAMBLE:  # chop preamble off the end
            data = data[:-len(PREAMBLE)]
        if data:  # if it times out, read_until returns empty bytes, so don't make it a message.
            message = Message()
            self.set_fields_general(message, data)
            return message

    def set_fields_general(self, message, data):
        try:
            message.data = data
            message.msgtype = data[0 : TYPE_LENGTH]
            payload_length_b = data[TYPE_LENGTH : TYPE_LENGTH + LENGTH_LENGTH]
            #message.payload_length = int.from_bytes(payload_length_b, ENDIAN)
            if message.msgtype == b'SS':
                message.payload_length = SS_PAYLOAD_LEN #workaround for wrong length field on SS message
            elif message.msgtype == b'RS':
                message.payload_length = RS_PAYLOAD_LEN #workaround for wrong length field on SS message
            message.payload = data[TYPE_LENGTH + LENGTH_LENGTH : TYPE_LENGTH + LENGTH_LENGTH + message.payload_length]
            message.checksum = int.from_bytes(data[TYPE_LENGTH + LENGTH_LENGTH + message.payload_length:], ENDIAN, signed=True)
            message.checksum_input = message.msgtype + payload_length_b + message.payload
            if self.check_valid(message):
                self.decode_payload_for_type(message, message.msgtype, message.payload)
        except Exception as e:
            message.valid = False
            message.error = "Parsing Error: "+str(e)

    def check_valid(self, message):
        try:
            # TODO handle other message types and lengths.
            if message.msgtype not in [b'RS', b'SS']:
                message.valid = False
                message.error = "Msgtype"
            elif message.payload_length + TYPE_LENGTH + LENGTH_LENGTH + CRC_LENGTH != len(message.data):
                message.valid = False
                message.error = "Length"
            elif not self.checksum_passes(message):
                message.valid = False
                message.error = "Checksum Fail"
            else:
                message.valid = True
                message.error = None
            return message.valid
        except Exception as err:
            print("exception checking message with data: "+str(message.data)+" , len = "+str(len(message.data)))
            message.valid = False
            message.error = "Check Error: "+str(err)

    def decode_payload_for_type(self, message, msgtype, payload):
        decoders = {b'RS': self.set_payload_fields_RS, b'SS': self.set_payload_fields_SS}
        decoderFunc = decoders.get(msgtype)
        decoderFunc(message, payload)

    def set_payload_fields_RS(self, message, payload):
        self.set_fields_from_list(message, RS_PAYLOAD_FIELDS, payload)
        try:
            #print("rs time math")
            message.time = message.seconds + (message.milliseconds * 1e-3) + (message.microseconds * 1e-6)
        except AttributeError as e:
            message.valid = False
            message.error = "missing time field: "+str(e)
        except Exception as e:
            message.valid = False
            message.error = "error in message time: " + str(e)

    def set_payload_fields_SS(self, message, payload):
        self.set_fields_from_list(message, SS_PAYLOAD_FIELDS, payload)
        try:
            #print("ss time math")
            message.time = message.seconds + (message.milliseconds * 1e-3) + (message.microseconds * 1e-6)
        except AttributeError as e:
            message.valid = False
            message.error = "missing time field: "+str(e)
        except Exception as e:
            message.valid = False
            message.error = "error in message time: " + str(e)

    # TODO this might also go in the message type handler
    def set_fields_from_list(self, message, format_list, data):
        try:
            format_str = "<" if ENDIAN == "little" else ">"
            attr_names = []
            for (name, format_code) in format_list:
                format_str += format_code
            values = struct.unpack(format_str, data)
            for i, (name, format_code) in enumerate(format_list):
                setattr(message, name, values[i])
        except Exception as e:
            print("error in set_fields_from_list")
            message.valid = False
            message.error = "Length(unpack): "+str(e)

    # load CRC code from a C libary made from crc32.c
    # update library: gcc -shared -o crc32.so -fPIC crc32.c
    def compute_checksum(self, message):
        check_in = message.checksum_input
        c_functions = CDLL(os.path.abspath("crc32.so"))
        return c_functions.CalculateBlockCRC32(len(check_in), check_in)

    def checksum_passes(self, message):
        return True #TODO - put this back in and include crc32.so
        #return self.compute_checksum(message) == message.checksum
