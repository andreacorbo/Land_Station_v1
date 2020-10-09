# main.py
# MIT license; Copyright (c) 2020 Andrea Corbo

import asyncio
import time
from datetime import datetime
import serial
import os
from ymodem import YMODEM
import config
import split_file
#ATDT3284135433

with serial.Serial(config.COM_PORT, config.BAUD_RATE, timeout=10, rtscts=False, xonxoff=False, ) as ser:

    def _getc(size, timeout=1):
        x = ser.read(size)
        if x:
            return x
        else:
            return False

    def _putc(data, timeout=1):
        x = ser.write(data)
        if x:
            return x
        else:
            return False

    def init():
        ser.reset_input_buffer()
        for at in [b'ATS0=1\r', b'AT&W\r']:
            ser.write(at)
            t0 = time.time()
            while True:
                if time.time() - t0 > config.CALL_TIMEOUT:
                    return False
                rxd = ser.read_until(b'\r\n')
                try:
                    rxd = rxd.decode("utf-8")
                except UnicodeError:
                    continue
                print(rxd)
                if "ERROR" in rxd:
                    return False
                if "OK" in rxd:
                    break
        return True

    def files_to_send():
        for root, subdirs, files in os.walk(config.SOFTWARE_DIR):
            for file in files:
                if file[0] not in (config.TMP_FILE_PFX, config.SENT_FILE_PFX):
                    yield os.path.join(root, file)
        if any (files for root, subdirs, files in os.walk(config.SOFTWARE_DIR)):
            yield "\x00"

    def hangup():
        ser.reset_input_buffer()
        for at in [b'+++', b'ATH\r']:
            ser.write(at)
            t0 = time.time()
            while True:
                if time.time() - t0 > config.CALL_TIMEOUT:
                    return False
                rxd = ser.read_until(b'\r\n')
                try:
                    rxd = rxd.decode("utf-8")
                except UnicodeError:
                    continue
                print(rxd)
                if "ERROR" in rxd:
                    return False
                if "OK" in rxd:
                    break
        return True

    if not config.DEBUG:
        init()
    ready = False
    connected = False
    rxd = ""
    ymodem = YMODEM(_getc, _putc, mode='Ymodem1k')
    while True:
        if not ready:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            split_file.main()
            print('########################################')
            print('#                                      #')
            print('#           YMODEM RECEIVER V1.1       #')
            print('#                                      #')
            print('########################################')
            ser.write(b'AT\r')
            ready = True
        if ser.in_waiting:
            rxd = ser.read_until(b'\r\n')
            try:
                rxd = rxd.decode("utf-8")
            except UnicodeError:
                continue
            if rxd:
                if "log.txt" in os.listdir():
                    filemode = "a"
                else:
                    filemode = "w"
                with open(config.LOG,filemode) as log:
                    log.write("{: " "<30}{}\r\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), rxd))
                if 'OK' in rxd:
                    print('READY')
                elif 'RING' in rxd and not config.AUTOANSWER:
                    ser.write(b'ATA\r')
                elif 'CONNECT' in rxd:
                    connected = True
                elif 'NO CARRIER' in rxd:
                    ready = False
                elif '+++' in rxd:
                    connected = False
                elif 'ATH' in rxd:
                    pass
                print(rxd)
                if connected:
                    ser.reset_input_buffer()
                    #time.sleep(1)
                    ymodem.recv(config.BUOY_DATA_DIR + config.RAW_DIR)
                    time.sleep(1)
                    #if files_to_send():
                    #   ymodem.send(files_to_send(), config.TMP_FILE_PFX, config.SENT_FILE_PFX)
                    #time.sleep(20)
                    #hangup()
                    connected = False
                    #ready = False
