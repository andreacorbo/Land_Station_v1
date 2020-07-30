import serial
from ymodem import YMODEM
import os
import time
from datetime import datetime
#ATDT3284135433
autoanswer = True
test_mode = False
byte = b''
word = ''
filename = ''
softwarepath = "software/"
datapath = "raw/"
logfile = "log.txt"

with serial.Serial('com4', 9600, timeout=10, rtscts=False, xonxoff=False, ) as ser:

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

    def files_to_send():
        tmp = []
        for dir in os.listdir(softwarepath):
            for file in os.listdir(softwarepath + dir):
                if file[0] not in ("$", "_"):  # check for unsent files
                    tmp.append(softwarepath + dir + '/' + file)
        return tmp

    def hangup():
        """Ends a call.

        Returns:
            True or False
        """
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        for at in [b'+++', b'ATH\r']:
            ser.write(at)
            t0 = time.time()
            while True:
                time.sleep(0.5)
                if time.time() - t0 == 10:
                    return False
                if ser.in_waiting:
                    rxd =ser.read()
                    print("\r\n{}".format(rxd.decode("utf-8")), end="")
                    if "ERROR" in rxd:
                        return False
                    if "OK" in rxd:
                        break
        return True

    rx = ''
    ready = False
    connected = False
    while True:
        if not ready:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            print('########################################')
            print('#                                      #')
            print('#           YMODEM RECEIVER V1.1       #')
            print('#                                      #')
            print('########################################')
            ser.write(b'AT\r')
            ready = True
        if ser.in_waiting:
            byte_ = ser.read(1)
            if byte_ == b'':
                continue
                #hangup()
            elif byte_ == b'\n':
                continue
            elif byte_ == b'\r':
                if rx:
                    if "log.txt" in os.listdir():
                        filemode = "a"
                    else:
                        filemode = "w"
                    print(rx)
                    with open(logfile,filemode) as log:
                        log.write("{: " "<30}{}\r\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"), rx))
                    if rx == 'OK':
                        print('READY')
                    elif rx == 'RING' and not autoanswer:
                        ser.write(b'ATA\r')
                    elif 'CONNECT' in rx:
                        time.sleep(5)
                        connected = True
                    elif rx == 'NO CARRIER':
                        ready = False
                    elif rx == '+++':
                        connected = False
                    elif rx == 'ATH':
                        pass
                        #ser.write(b'OK\r')
                    if connected and not test_mode:
                        ser.read(1)  # Clear last byte \n
                        modem = YMODEM(_getc, _putc, mode='Ymodem1k')
                        #if not modem.recv(datapath):
                        #    connected = False
                        #    ready = False
                        modem.recv(datapath)
                        time.sleep(2)
                        modem.send(files_to_send(), "$", "_")
                        connected = False
                        ready = False
                    rx = ''
            else:
                rx += chr(ord(byte_))
