# main.py
# MIT license; Copyright (c) 2020 Andrea Corbo

import serial
from ymodem import YMODEM
import os
import time
from datetime import datetime
import cfg
import split_file
# 3284135433 COM4 Wavecom Boe
# 3358489872 COM3 Siemens Isonzo
# 3284135443 MAMBO2
# 3355083535 ?

with serial.Serial('/dev/modem', 115200, timeout=10, rtscts=False, xonxoff=False) as s:
    i = 0
    while True:
        x=s.read(2)
        if x != b'\x00\x00':
            i += 1
            print(i, x)
        s.write(b'\x06')
