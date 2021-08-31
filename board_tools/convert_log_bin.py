import sys
import pathlib
parent_dir = str(pathlib.Path(__file__).parent)
sys.path.append(parent_dir+'/src')
from tools import *
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from user_program_config import *

#csv top line with variable names
complete_header = ",".join(EXPORT_COMPLETE_FIELDS)
fog_header = ",".join(EXPORT_FOG_FIELDS)

#default values: currently 0 for everything. could set a different value per field and message type
def complete_defaults(name):
    return 0

def fog_defaults(name):
    return 0

def format_field(var_name, value):
    # float: force decimal since Kepler.gl will turn exponential notation into "string"
    if type(value) is float:
        return "{:.10f}".format(value).rstrip('0').rstrip('.')
    # can do more conditions using var_name and msgtype here. what about time formats?
    else:
        return str(value)

def export_logs():
    message_scheme = ByteScheme()

    # open the targeted log file
    Tk().withdraw()
    default_dir = os.path.join(os.path.dirname(__file__), "../logs")
    input_path = askopenfilename(initialdir=default_dir, title="Select log to convert")
    if not input_path: # empty on cancel
        print("cancelled")
        exit() # in user program, return to main menu instead

    reader = FileReaderConnection(input_path)

    # pick name and location for output files
    input_filename = os.path.basename(input_path) # should it take off the .txt or other extension?
    if "." in input_filename:
        input_notype = input_filename[:input_filename.find(".")] # before the .
    else:
        input_notype = input_filename

    # create new csv files
    export_path = os.path.join(os.path.dirname(__file__), "..", "exports", input_notype) # exports directory
    os.makedirs(export_path, exist_ok=True)

    fog_file_path = os.path.join(export_path, "fog.csv")
    fog_out = open(fog_file_path, 'w')  # will overwrite the csv if it already exists
    print("exporting to " + os.path.normpath(fog_file_path))
    fog_out.write(fog_header)

    complete_file_path = os.path.join(export_path, "complete.csv")
    complete_out = open(complete_file_path, 'w')  # will overwrite the csv if it already exists
    print("exporting to " + os.path.normpath(complete_file_path))
    complete_out.write(complete_header)

    reader.read_until(PREAMBLE) #take off first preamble
    line = reader.read_until(PREAMBLE) #actual first line - read until second preamble
    line = line.strip(PREAMBLE) #take off that second preamble

    line_num = 0
    while line: #until read empty
        #show progress: dot per some number of lines
        line_num += 1
        if line_num % 10000 == 0:
            print(".", end="")

        m = message_scheme.parse_message(line)
        if m and m.valid:
            #write each set of attributes to the right csv
            for (outfile, fields, defaults) in [(complete_out, EXPORT_COMPLETE_FIELDS, complete_defaults),
                                                (fog_out, EXPORT_FOG_FIELDS, fog_defaults)]:
                out_list = []
                for name in fields:  # or show_fields[m.msgtype]
                    if hasattr(m, name):
                        value = getattr(m, name)
                        out_list.append(format_field(name, value))
                    else:
                        # out_list.append(str(defaults(name)))
                        out_list.append(str(defaults(name)))
                out_line = "\n" + ",".join(out_list)
                outfile.write(out_line)
        else:
            pass
            #print("invalid message: "+str(message))

        line = reader.read_until(PREAMBLE) #next message: read until next preamble, not including that preamble
        line = line.strip(PREAMBLE)

    reader.close()
    fog_out.close()
    complete_out.close()

if __name__ == "__main__":
    #TODO - add more command line args with different options?
    export_logs()