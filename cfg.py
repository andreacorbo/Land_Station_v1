# cfg.py
# MIT license; Copyright (c) 2020 Andrea Corbo

######################### global ###############################################
RAW_DIR = 'raw/'
CALL_TIMEOUT = 60
######################### main.py #############################################
DEBUG = False
if DEBUG:
    COM_PORT = '/dev/dpi'
    BAUD_RATE = 9600
else:
    COM_PORT = 'COM4'
    BAUD_RATE = 9600
AUTOANSWER = False
SOFTWARE_DIR = 'software/'
LOG = 'log.txt'
INIT_ATS = [b'ATH\r',b'ATE1\r',b'ATI\r',b'AT+CREG=0\r',b'AT+COPS=1,2,22201\r',b'AT+CSQ\r',b'AT+CBST=7,0,1\r',b'ATS0=1\r',b'AT+CLIP=1\r',b'AT&W\r']
RETRY = 2
######################### send.py ##############################################
CALL_ATS = [b'ATD3284388140\r']  # MAMBO2
HANGUP_ATS = [b'+++', b'ATH\r']
ATS_DELAY = 1
CALL_ATTEMPT = 3
######################### split_file.py ########################################
BUOY_ID = {
    '300' : 'MAMBO_2',
    '400' : 'MAMBO_3',
    '500' : 'MAMBO_4',
    '000' : 'MAMBO_0'
}
BUOY_DATA_DIR = './boe/PC_Boe_Stazione_di_terra_runtime/'
BUOY_RT_DIR = 'rt/'
BUOY_MSTAT_DIR = 'mstat/'
BUOY_GPRMC_DIR = 'gprmc/'
ADCP_DATA_DIR = './correntometri_aquapro/rtdata/'
GARBAGE_DATA_DIR = 'garbage/'
DEBUG_FOLDER_PFX = ''
ARCHIVED_FILE_PFX = '_'
TMP_FILE_PFX = '$'
SENT_FILE_PFX = '#'
DATA_FILE_EXT = '.txt'
