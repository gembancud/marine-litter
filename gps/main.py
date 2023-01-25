import time
import math
import sys

sys.path.append(".")
from . import L76X

x = L76X.L76X()
x.L76X_Set_Baudrate(9600)
x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
x.L76X_Set_Baudrate(115200)

x.L76X_Send_Command(x.SET_POS_FIX_400MS)

# Set output message
x.L76X_Send_Command(x.SET_NMEA_OUTPUT)


x.L76X_Exit_BackupMode()
x.L76X_Gat_GNRMC()


def gps():
    if x.Status == 1:
        print("Already positioned")
    else:
        print("No positioning")
        return
    value_lon = x.Lon
    value_lat = x.Lat
    return value_lon, value_lat


def gps_cleanup():
    GPIO.cleanup()
