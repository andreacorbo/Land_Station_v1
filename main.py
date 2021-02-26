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

with serial.Serial(cfg.COM_PORT, cfg.BAUD_RATE, timeout=10, rtscts=False, xonxoff=False) as s:

    def getc(size, timeout=1):
        s.timeout = timeout
        res = s.read(size)
        if res:
            return res
        return None

    def putc(data, timeout=1):
        s.write_timeout = timeout
        res = s.write(data)
        if res:
            return res
        return None

    def init():
        print('INITIALIZING MODEM...')
        s.reset_input_buffer()
        for at in cfg.INIT_ATS:
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

    def hangup():
        tout = s.timeout
        s.timeout = 2
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
                if b'' in rxd:
                    ret = True
                    break
        s.timeout = tout

    def files_to_send():
        for root, subdirs, files in os.walk(os.getcwd()):
            for f in files:
                if f[0] not in (cfg.TMP_FILE_PFX, cfg.SENT_FILE_PFX):
                    yield os.path.join(root, f)
        #if any (files for root, subdirs, files in os.walk(os.getcwd())):
        yield '\x00'

    # Gets caller identity.
    def preamble():
        for _ in range(30):
            res = getc(6,10)
            if res is not None:
                res = res.decode('utf-8')
                print('<-- {}'.format(res))
                if res.startswith('mambo'):
                    print('ACK -->')
                    putc(b'\x06')  # ACK
                    return res
                else:
                    print('NAK -->')
                    putc(b'\x15')  # NACK
                    return False
        return False


    #if not cfg.DEBUG:
    #    init()  # Initializes modem.
    ready = False
    connected = False
    rxd = ''
    ymodem = YMODEM(getc, putc, 6, 30)
    while True:
        if not ready:
            s.reset_input_buffer()
            s.reset_output_buffer()
            if cfg.SPLIT_FILES:
                split_file.main()
            print('########################################')
            print('#                                      #')
            print('#             YMODEM V1.1              #')
            print('#                                      #')
            print('########################################')
            try:
                hangup()  # Hangup if still connected.
            except:
                pass
            ready = True
        if s.in_waiting:
            rxd = s.read_until(b'\r\n')
            try:
                rxd.decode('utf-8')[:-2]
            except UnicodeError:
                continue
            print(rxd.decode('utf-8')[:-2])
            if 'log.txt' in os.listdir():
                filemode = 'a'
            else:
                filemode = 'w'
            with open(cfg.LOG,filemode) as log:
                log.write('{: ' '<30}{}\r\n'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), rxd.decode('utf-8')[:-2]))
            if b'OK' in rxd:
                print('READY')
            elif b'RING' in rxd and not cfg.AUTOANSWER:
                s.write(b'ATA\r')
            elif b'CONNECT' in rxd:
                connected = True
            elif b'NO CARRIER' in rxd:
                ready = False
            elif b'+++' in rxd:
                connected = False
            elif b'ATH' in rxd:
                pass
            if connected:
                s.reset_input_buffer()
                try:
                    root = os.getcwd()
                    remote = preamble()
                    if remote:
                        os.chdir(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + remote)  # Moves to caller home.
                        print('CWD {}'.format(os.getcwd()))
                        ymodem.recv()
                        time.sleep(1)
                        os.chdir(os.getcwd() + '/' + cfg.SOFTWARE_DIR)  # Moves to sofware directory.
                        print('CWD {}'.format(os.getcwd()))
                        if files_to_send():
                            ymodem.send(files_to_send())
                        os.chdir(root)
                except Exception as err:
                    print(err)
                    #hangup()
                ready = False
                connected = False
        time.sleep(0.1)
