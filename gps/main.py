import time
import math
import multiprocessing
import sys

sys.path.append(".")
from . import L76X


class GPS:
    lat = multiprocessing.Value("f", -1)
    lon = multiprocessing.Value("f", -1)

    def __init__(self):
        self.process = multiprocessing.Process(
            target=self.loop, args=(self.lon, self.lat)
        )

    def start(self):
        self.process.start()

    @staticmethod
    def loop(lon, lat):
        x = L76X.L76X()
        x.L76X_Set_Baudrate(9600)
        x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
        time.sleep(2)
        x.L76X_Set_Baudrate(115200)

        x.L76X_Send_Command(x.SET_POS_FIX_400MS)

        # Set output message
        x.L76X_Send_Command(x.SET_NMEA_OUTPUT)

        x.L76X_Exit_BackupMode()

        while True:
            x.L76X_Gat_GNRMC()
            lon.value = x.Lon
            lat.value = x.Lat


def loop(lon, lat):
    x = L76X.L76X()
    x.L76X_Set_Baudrate(9600)
    x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
    time.sleep(2)
    x.L76X_Set_Baudrate(115200)

    x.L76X_Send_Command(x.SET_POS_FIX_400MS)

    # Set output message
    x.L76X_Send_Command(x.SET_NMEA_OUTPUT)

    x.L76X_Exit_BackupMode()

    while True:
        x.L76X_Gat_GNRMC()
        lon.value = x.Lon
        lat.value = x.Lat
        time.sleep(1)
