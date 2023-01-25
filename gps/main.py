import time
import math
import sys

sys.path.append(".")
from . import L76X


class GPS:
    gps = None
    interval = 1
    last_executed = 0
    
    def __init__(self):
        x = L76X.L76X()
        x.L76X_Set_Baudrate(9600)
        x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
        time.sleep(2)
        x.L76X_Set_Baudrate(115200)

        x.L76X_Send_Command(x.SET_POS_FIX_400MS)

# Set output message
        x.L76X_Send_Command(x.SET_NMEA_OUTPUT)

        x.L76X_Exit_BackupMode()

        self.gps = x
        self.last_executed = time.time()

    def __call__(self):
        if time.time() - self.last_executed < self.interval:
            return -1, -1
        self.gps.L76X_Gat_GNRMC()
        value_lon = self.gps.Lon
        value_lat = self.gps.Lat
        
        # save time stamp last executed
        self.last_executed = time.time()

        return value_lon, value_lat
        