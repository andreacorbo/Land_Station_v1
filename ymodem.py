# ymodem.py
# MIT license; Copyright (c) 2020 Andrea Corbo

import time
import datetime
import os
import sys
from functools import partial
################################################################################
# Protocol bytes
################################################################################
SOH = b'\x01'  # 1
STX = b'\x02'  # 2
EOT = b'\x04'  # 4
ACK = b'\x06'  # 6
NAK = b'\x15'  # 21
CAN = b'\x18'  # 24
C = b'\x43'  # 67
PAD = b'\x1a'
################################################################################
# File identifiers
################################################################################
#BPFX = 'B'      # Backup file prefix
TPFX = '$'      # Temp file prefix
SPFX = '#'      # Sent file prefix
################################################################################
# crctab calculated by Mark G. Mendel, Network Systems Corporation
################################################################################
CRC_TAB = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
]

class YMODEM:

    def __init__(self, getc, putc, retry=3, timeout=10, mode='Ymodem1k'):
        self.getc = getc
        self.putc = putc
        self.retry = retry
        self.tout = timeout
        self.mode = mode

    buoyId = {
        '300' : 'MAMBO_2',
        '400' : 'MAMBO_3',
        '500' : 'MAMBO_4'
    }


    ############################################################################
    # Receiver.
    ############################################################################
    def recv(self, crc_mode=1):

        def log(msg):
            utc = datetime.datetime.utcnow().strftime('%H:%M:%S')
            print('{} {}'.format(utc,msg))

        # Writes out data to the passed file.
        # Runs in a separate thread to not block scheduler.
        def w_data(file, data):
            try:
                with open(file, 'ab') as s:
                    s.write(data)
                return True
            except:
                log('ERROR OPENING {}'.format(file))
                return False

        def cancel():
            log('CANCEL TRANSMISSION...')
            for _ in range(2):
                self.putc(CAN, 60)
                log('CAN -->')
                time.sleep(1)

        def ack():
            ec = 0
            while True:
                if ec > self.retry:
                    log('TOO MANY ERRORS, ABORTING...')
                    return False
                if not self.putc(ACK, self.tout):
                    log('ERROR SENDING ACK, RETRY...')
                    ec += 1
                else:
                    log('ACK -->')
                    return True
                time.sleep(1)

        def nak():
            ec = 0
            while True:
                if ec > self.retry:
                    log('TOO MANY ERRORS, ABORTING...')
                    return False
                if not self.putc(NAK, self.tout):
                    log('ERROR SENDING NAK, RETRY...')
                    ec += 1
                else:
                    log('NACK -->')
                    return True
                time.sleep(1)

        # Clear to receive.
        def ctr():
            ec = 0
            while True:
                if ec > self.retry:
                    log('TOO MANY ERRORS, ABORTING...')
                    return False
                if not self.putc(C, self.tout):
                    log('ERROR SENDING C, RETRY...')
                    ec += 1
                else:
                    log('C -->')
                    return True
                time.sleep(1)

        # Validate checksum.
        def v_cksum(data, crc_mode):

            def calc_cksum(data, cksum=0):
                return (sum(map(ord, data)) + cksum) % 256

            # Calculates the 16 bit Cyclic Redundancy Check for a given block of data.
            def calc_crc(data, crc=0):
                for c in bytearray(data):
                    crctbl_idx = ((crc >> 8) ^ c) & 0xff
                    crc = ((crc << 8) ^ CRC_TAB[crctbl_idx]) & 0xffff
                return crc & 0xffff

            if crc_mode:
                cksum = bytearray(data[-2:])
                recv = (cksum[0] << 8) + cksum[1]
                data = data[:-2]
                calc = calc_crc(data)
                valid = bool(recv == calc)
                if not valid:
                    log('CRC FAIL EXPECTED({:04x}) GOT({:4x})'.format(recv, calc))
            else:
                cksum = bytearray([data[-1]])
                recv = cksum[0]
                data = data[:-1]
                calc = calc_cksum(data)
                valid = recv == calc
                if not valid:
                    log('CHECKSUM FAIL EXPECTED({:02x}) GOT({:2x})'.format(recv, calc))
            return valid, data

        #def set_path(filepath):
        #    # Land Station only
        #    station = filepath.split('/')[0]
        #    file = filepath.split('/')[1]
        #    id = {v.replace('_',''):k for k,v in self.buoyId.items()}[station.upper()]
        #    new_file = 'Nmea_Data_ID_' + id + '_' + file + '.txt'
        #    return ('/' + id + '_' + self.buoyId[id] + '/data/' + new_file)

        ########################################################################
        # Transaction starts here
        ########################################################################
        ec = 0  # Error counter.
        log('REQUEST 16 BIT CRC')
        while True:
            if crc_mode:
                while True:
                    if ec == (self.retry // 2):
                        log('REQUEST STANDARD CHECKSUM')
                        crc_mode = 0
                        break
                    if not self.putc(C):  # Sends C to request 16 bit CRC as first choice.
                        log('ERROR SENDING C, RETRY...')
                        ec += 1
                    else:
                        log('C -->')
                        break
            if not crc_mode and ec < self.retry:
                if not nak():  # Sends NAK to request standard checksumum as fall back.
                    return False
            #
            # Receives packets.
            #
            sz = 128  # Packet size.
            cc = 0   # Cancel counter.
            seq = 0  # Sequence counter.
            isz = 0  # Income size.
            sf = False  # Start flag
            while True:
                c = self.getc(1,self.tout)
                if ec == self.retry:
                    log('TOO MANY ERRORS, ABORTING')
                    cancel()  # Cancels transmission.
                    return False
                elif not c and not sf:
                    log('TIMEOUT OCCURRED WHILE STARTING')
                    ec += 1
                    break  # Resends start byte.
                elif not c and sf:
                    log('TIMEOUT OCCURRED WHILE RECEIVING')
                    ec += 1
                elif c == CAN:
                    log('<-- CAN')
                    if cc:
                        log('TRANSMISSION CANCELED BY SENDER')
                        return False
                    else:
                        cc = 1
                        ec = 0  # Ensures to receive a second CAN.
                elif c == SOH:
                    sf = True
                    log('SOH <--')
                    if sz != 128:
                        sz = 128
                        log('USING 128 BYTES PACKET SIZE')
                elif c == STX:
                    sf = True
                    log('STX <--')
                    if sz != 1024:
                        sz = 1024
                        log('USING 1 KB PACKET SIZE')
                elif c == EOT:
                    log('EOT <--')
                    if not ack():  # Acknowledges EOT.
                        return False
                    seq = 0
                    isz = 0
                    if not ctr():  # Clears to receive.
                        return False
                    ec = 0
                    continue
                else:
                    log('UNATTENDED CHAR {}'.format(c))
                    ec += 1
                    continue
                #
                # Reads packet sequence.
                #
                ec = 0
                while True:
                    seq1 = self.getc(1, self.tout)
                    if not seq1:
                        log('FAILED TO GET FIRST SEQUENCE BYTE')
                        seq2 = None
                    else:
                        seq1 = ord(seq1)
                        seq2 = self.getc(1, self.tout)
                        if not seq2:
                            log('FAILED TO GET SECOND SEQUENCE BYTE')
                        else:
                            seq2 = 0xff - ord(seq2)
                            log('PACKET {} <--'.format(seq))
                    if not (seq1 == seq2 == seq):
                        log('SEQUENCE ERROR, EXPECTED {} GOT {}, DISCARD DATA'.format(seq, seq1))
                        self.getc(sz + 1 + crc_mode)  # Discards data packet.
                        if seq1 == 0:  # If receiving file name packet, clears for transmission.
                            if not ctr():
                                return False
                            ec = 0
                    else:
                        data = self.getc(sz + 1 + crc_mode, self.tout)
                        valid, data = v_cksum(data, crc_mode)
                        if not valid:
                            if not nak():  # Requests retransmission.
                                return False
                            ec = 0
                        else:
                            if seq == 0:  # Sequence 0 contains file name.
                                if data == bytearray(sz):  # Sequence 0 with null data state end of trasmission.
                                    if not ack():  # Acknowledges EOT.
                                        return False
                                    log('END OF TRANSMISSION')
                                    return True
                                ds = []  # Data string.
                                df = ''  # Data field.
                                for b in data:
                                    if b != 0:
                                        df += chr(b)
                                    elif len(df) > 0:
                                        ds.append(df)
                                        df = ''
                                fname = ds[0]
                                log(ds)
                                length = int(ds[1].split(' ')[0])
                                log('RECEIVING FILE {}'.format(fname))
                                if not ack():  # Acknowledges packet.
                                    return False
                                if not ctr():  # Clears for transmission.
                                    return False
                                ec = 0
                            else:
                                tn = isz - length  # Counts trailing null chars.
                                if not w_data(fname, data[:-tn]):
                                    if not nak():  # Requests retransmission.
                                        return False
                                    ec += 1
                                else:
                                    if not ack():
                                        return False
                                    isz += len(data)
                                    ec = 0
                            seq = (seq + 1) % 0x100  # Calcs next expected seq.
                    break

    ############################################################################
    # Sender.
    ############################################################################
    def send(self, files):

        def log(msg):
            utc = datetime.datetime.utcnow().strftime('%H:%M:%S')
            print('{} {}'.format(utc,msg))

        # Reads out n-bytes from the current file.
        def r_data(file,ptr,sz):
            try:
                with open(file) as s:
                    s.seek(ptr)
                    data = s.read(sz)
                    tptr = s.tell()
            except:
                pass
            return (data,tptr)

        # Saves last read byte.
        def set_lb(tmpf,ptr):
            with open(tmpf, 'w') as t:
                t.write(str(ptr))

        # Gets last read byte.
        def get_lb(tmpf):
            try:
                with open(tmpf) as t:
                    ptr = int(t.read())
            except:
                ptr = 0  # File not exists.
            return ptr

        # Backups the current daily file for asyncronous access.
        #def bkp_f(file):
            #bkp = file.replace(file.split('/')[-1], BPFX + file.split('/')[-1])
            #with f_lock:
            #    shutil.copyfile(file, bkp)
            #return bkp

        # Gets file info.
        def stat_f(file):
            fstat = os.stat(file)
            return fstat

        def mk_file_hdr(sz):
            b = []
            if sz == 128:
                b.append(ord(SOH))
            elif sz == 1024:
                b.append(ord(STX))
            b.extend([0x00, 0xff])
            return bytearray(b)

        def mk_data_hdr(seq,sz):
            assert sz in (128, 1024), sz
            b = []
            if sz == 128:
                b.append(ord(SOH))
            elif sz == 1024:
                b.append(ord(STX))
            b.extend([seq, 0xff - seq])
            return bytearray(b)

        # Makes the checksum for the current packet.
        def mk_cksum(data,crc_mode):

            def calc_cksum(data, cksum=0):
                return (sum(map(ord, data)) + cksum) % 256

            #Calculates the 16 bit Cyclic Redundancy Check for a given block of data.
            def calc_crc(data, crc=0):
                for c in bytearray(data):
                    crctbl_idx = ((crc >> 8) ^ c) & 0xff
                    crc = ((crc << 8) ^ CRC_TAB[crctbl_idx]) & 0xffff
                return crc & 0xffff

            b = []
            if crc_mode:
                crc = calc_crc(data)
                b.extend([crc >> 8, crc & 0xff])
            else:
                crc = calc_cksum(data)
                b.append(crc)
            return bytearray(b)

        # Archives totally sent files.
        def totally_sent(file,sntf,tmpf):

            #def is_new_day(file):
            #    today = time.time() - time.time() % 86400
            #    try:
            #        last_file_write = os.stat(file)[8] - os.stat(file)[8] % 86400
            #        if today - last_file_write >= 86400:
            #            return True
            #        return False
            #    except:
            #        return False

            #if is_new_day(file):
            try:
                os.rename(file, sntf)
                try:
                    os.remove(tmpf)
                except:
                    log('UNABLE TO REMOVE FILE {}'.format(tmpf))
            except:
                log('UNABLE TO RENAME FILE {}'.format(file))

        # Clear to send.
        def cts():
            ec = 0
            while True:
                if ec > self.retry:
                    log('TOO MANY ERRORS, ABORTING...')
                    return  False
                c = self.getc(1, self.tout)
                if not c:
                    log('TIMEOUT OCCURRED, RETRY...')
                    ec += 1
                elif c == C:
                    log('<-- C')
                    return True
                else:
                    log('UNATTENDED CHAR {}, RETRY...'.format(c))
                    ec += 1

        ########################################################################
        # Transaction starts here
        ########################################################################
        try:
            sz = dict(Ymodem = 128, Ymodem1k = 1024)[self.mode]  # Packet size.
        except KeyError:
            raise ValueError('INVALID MODE {}'.format(self.mode))
        #
        # Waits for receiver.
        #
        ec = 0  # Error counter.
        log('BEGIN TRANSACTION, PACKET SIZE {}'.format(sz))
        while True:
            if ec > self.retry:
                log('TOO MANY ERRORS, ABORTING...')
                return False
            c = self.getc(1, self.tout)
            if not c:
                log('TIMEOUT OCCURRED WHILE WAITING FOR STARTING TRANSMISSION, RETRY...')
                ec += 1
            elif c == C:
                log('<-- C')
                log('16 BIT CRC REQUESTED')
                crc_mode = 1
                break
            elif c == NAK:
                log('<-- NAK')
                log('STANDARD CECKSUM REQUESTED')
                crc_mode = 0
                break
            else:
                log('UNATTENDED CHAR {}, RETRY...'.format(c))
                ec += 1
        #
        # Iterates over file list.
        #
        fc = 0  # File counter.
        for f in files:
            # Temporary files store only the count of sent bytes.
            tmpf = f.replace(f.split('\\')[-1], TPFX + f.split('\\')[-1])
            # Sent files get renamed in order to be archived.
            sntf = f.replace(f.split('\\')[-1], SPFX + f.split('\\')[-1])
            fname = '/'.join(f.split('\\')[-2:])
            if f != '\x00':
                ptr = get_lb(tmpf)
                if ptr == int(os.stat(f)[6]):  # Check if eof.
                    log('FILE {} ALREADY TRANSMITTED, SEND NEXT FILE...'.format(fname))
                    totally_sent(f,sntf,tmpf)
                    continue
            fc += 1
            #
            # If multiple files waits for clear to send.
            #
            if fc > 1:
                if not cts():
                    return False
            #
            # Create file name packet
            #
            hdr = mk_file_hdr(sz)
            data = bytearray(fname + '\x00', 'utf8')  # self.fname + space
            if f != '\x00':
                fstat = stat_f(f)
                data.extend((
                    str(fstat[6] - ptr) +
                    ' ' +
                    str(fstat[8])
                    ).encode('utf8'))  # Sends data size and mod date.
            pad = bytearray(sz - len(data))  # Fills packet size with nulls.
            data.extend(pad)
            cksum = mk_cksum(data,crc_mode)
            while True:
                #
                # Sends filename packet.
                #
                ec = 0
                while True:
                    if ec > self.retry:
                        log('TOO MANY ERRORS, ABORTING...')
                        return  False
                    if not self.putc(hdr + data + cksum, self.tout):
                        ec += 1
                        continue
                    break
                log('SENDING FILE {}'.format(fname))
                #
                # Waits for reply to filename paket.
                #
                ec = 0
                cc = 0  # Cancel counter.
                ackd = 0  # Acked.
                while True:
                    c = self.getc(1, 2)
                    #if ec > self.retry:
                    if ec > 20:  # DEBUG
                        log('TOO MANY ERRORS, ABORTING...')
                        return  False
                    #c = self.getc(1, self.tout)
                    if not c:  # handle rx erros
                        log('TIMEOUT OCCURRED, RETRY...')
                        ec += 1
                        continue
                    elif c == ACK:
                        log('<-- ACK TO FILE {}'.format(fname))
                        if data == bytearray(sz):
                            log('TRANSMISSION COMPLETE, EXITING...')
                            return True
                        else:
                            ackd = 1
                            break
                    elif c == NAK:
                        log('<-- NAK'.format(fname))
                        ec += 1
                        break  # Resends packet.
                    elif c == CAN:
                        log('<-- CAN')
                        if cc:
                            log('TRANSMISSION CANCELED BY RECEIVER')
                            return  False
                        else:
                            cc = 1
                            continue  # Waits for a second CAN
                    else:
                        log('UNATTENDED CHAR {}, RETRY...'.format(c))
                        ec += 1
                        #break  # Resends packet.
                if ackd:
                    break  # Waits for data.
            if f == '\x00':
                return True
            #
            # Waits for clear to send.
            #
            if not cts():
                return False
            #
            # Sends file.
            #
            sc = 0  # Succeded counter.
            pc = 0  # Packets counter.
            seq = 1
            while True:
                data, tptr = r_data(f,ptr,sz)
                if not data:
                    log('EOF')
                    break
                pc += 1
                hdr = mk_data_hdr(seq,sz)
                fst = '{:' + PAD.decode('utf-8') + '<' + str(sz) + '}'  # Right fills data with pad byte.
                data = fst.format(data)
                data = data.encode('utf8')
                cksum = mk_cksum(data,crc_mode)
                while True:
                    #
                    # Send data packet.
                    #
                    ec = 0
                    while True:
                        if ec > self.retry:
                            log('TOO MANY ERRORS, ABORTING...')
                            return  False
                        if not self.putc(hdr + data + cksum, self.tout):
                            ec += 1
                            continue  # Resend packet.
                        else:
                            log('PACKET {} -->'.format(seq))
                            break
                    #
                    # Waits for reply.
                    #
                    ec = 0
                    cc = 0
                    ackd = 0
                    while True:
                        if ec > self.retry:
                            log('TOO MANY ERRORS, ABORTING...')
                            return  False
                        c = self.getc(1, self.tout)
                        if not c:
                            log('TIMEOUT OCCURRED, RETRY...')
                            ec += 1
                            break
                        elif c == ACK:
                            log('<-- ACK TO PACKET {}'.format(seq))
                            set_lb(tmpf,ptr)
                            ackd = 1
                            sc += 1
                            ptr = tptr  # Updates pointer.
                            seq = (seq + 1) % 0x100
                            break
                        elif c == NAK:
                            log('<-- NAK')
                            ec += 1
                            break  # Resends packet.
                        elif c == CAN:
                            log('<-- CAN')
                            if cc:
                                log('TRANSMISSION CANCELED BY RECEIVER')
                                return  False
                            else:
                                cc = 1
                                continue  # Waits for a second CAN.
                        else:
                            log('UNATTENDED CHAR {}, RETRY...'.format(c))
                            ec += 1
                            break  # Resends last packet.
                    if ackd:
                        break  # Sends next packet
            #
            # End of transmission.
            #
            ec = 0
            while True:
                if ec > self.retry:
                    log('TOO MANY ERRORS, ABORTING...')
                    return False
                if not self.putc(EOT, self.tout):
                    ec += 1
                    continue  # resend EOT
                log('EOT -->')
                c = self.getc(1, self.tout)  # waiting for reply
                if not c:  # handle rx errors
                    log('TIMEOUT OCCURRED WHILE WAITING FOR REPLY TO EOT, RETRY...')
                    ec += 1
                elif c == ACK:
                    log('<-- ACK TO EOT')
                    log('FILE {} SUCCESSFULLY TRANSMITTED'.format(fname))
                    totally_sent(f,sntf,tmpf)
                    break  # Sends next file.
                else:
                    log('UNATTENDED CHAR {}, RETRY...'.format(c))
                    ec += 1

YMODEM1k = partial(YMODEM, mode='Ymodem1k')
