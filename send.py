import serial
from ymodem import YMODEM
import os
import time
from datetime import datetime

with serial.Serial("/dev/modem", 115200, timeout=10, rtscts=False, xonxoff=False, ) as ser:

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
        for dir in os.listdir(config.SOFTWARE_DIR):
            for file in os.listdir(config.SOFTWARE_DIR + dir):
                if file[0] not in ("$", "_"):  # check for unsent files
                    yield config.SOFTWARE_DIR + dir + '/' + file
        if any(file[0] not in (config.TMP_FILE_PFX, config.SENT_FILE_PFX) for file in os.listdir(config.SOFTWARE_DIR)):
                yield "\x00"

    def call():
        ser.reset_input_buffer()
        for at in config.CALL_ATS:
            ser.write(at)
            t0 = time.time()
            rxd = ""
            while time.time() - t0 < config.CALL_TIMEOUT:
                if ser.in_waiting:
                    byte = ser.read(1)
                    if byte == b'':
                        continue
                    elif byte == b'\n':
                        continue
                    elif byte == b'\r':
                        if rxd:
                            print(rxd)
                            if "ERROR" in rxd:
                                return False
                            if "NO CARRIER" in rxd:
                                return False
                            if "NO ANSWER" in rxd:
                                return False
                            if "OK" in rxd:
                                break
                            if "CONNECT" in rxd:
                                ser.read(1)  # Clears last byte \n
                                return True
                            rxd = ""
                    else:
                        rxd += chr(ord(byte))
            return False
            time.sleep(config.ATS_DELAY)

    def hangup():
        ser.reset_input_buffer()
        for at in config.HANGUP_ATS:
            ser.write(at)
            t0 = time.time()
            rxd = ""
            while time.time() - t0 < config.CALL_TIMEOUT:
                if ser.in_waiting:
                    byte = ser.read(1)
                    if byte == b'':
                        continue
                    elif byte == b'\n':
                        continue
                    elif byte == b'\r':
                        if rxd:
                            if "ERROR" in rxd:
                                return False
                            if "OK" in rxd:
                                break
                            print(rxd)
                            rxd = ""
                    else:
                        rxd += chr(ord(byte))
            return False
        return True

    def data_transfer():
        """Sends files over the gsm network."""
        connected = False
        for _ in range(config.CALL_ATTEMPT):
            if call():
                modem = YMODEM(_getc, _putc, mode='Ymodem1k')
                modem.send(files_to_send(), config.TMP_FILE_PFX, config.SENT_FILE_PFX)
                hangup()
        return

    data_transfer()
