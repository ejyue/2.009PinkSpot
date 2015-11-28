#buttons are light tap not push
# Pan Degree: 540 deg
# Movement Speed:

import pysimpledmx # make sure it ais in same home directory
import time

COMport = "/dev/cu.usbserial-ENYXTLPV" # define COMport number

mydmx = pysimpledmx.DMXConnection(COMport) # create dmx object
