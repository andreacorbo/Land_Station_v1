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
# 3284135443 ?
# 3355083535 ?

with serial.Serial(cfg.COM_PORT, cfg.BAUD_RATE, timeout=10, rtscts=False, xonxoff=False) as s:

    # Make a call.
    def call():
        s.reset_input_buffer()
        s.write(b'ATD3284388140\r')
        while True:
            rxd = s.read_until(b'\r\n')
            try:
                rxd.decode('utf-8')
            except UnicodeError:
                print('non utf')
            print(rxd.decode('utf-8'))
            if rxd.startswith(b'CONNECT'):
                return True
        return False

    def hangup():
        s.reset_input_buffer()
        for at in cfg.HANGUP_ATS:
            ret = True
            i = 0
            while i < cfg.RETRY:
                if ret:
                    time.sleep(1)
                    s.write(at)
                rxd = s.read_until(b'\r\n')
                try:
                    rxd.decode('utf-8')
                except UnicodeError:
                    continue
                print(rxd.decode('utf-8'))
                if at in rxd:
                    ret = False
                if b'ERROR' in rxd:
                    ret = True
                    i += 1
                    continue
                if b'OK' in rxd:
                    ret = True
                    break

    if call():
        while True:
            s.write(b'\x18')
            time.sleep(1)
