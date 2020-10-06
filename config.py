######################### global ###############################################
RAW_DIR = "raw/"
CALL_TIMEOUT = 60
######################### modem.py #############################################
DEBUG = False
if DEBUG:
    COM_PORT = "/dev/dpi"
    BAUD_RATE = 9600
else:
    COM_PORT = "/dev/modem"
    BAUD_RATE = 115200
AUTOANSWER = True
SOFTWARE_DIR = "software/"
LOG = "log.txt"
######################### send.py ##############################################
CALL_ATS = [b"ATD3284135433\r"]
HANGUP_ATS = [b"+++", b"ATH\r"]
ATS_DELAY = 1
CALL_ATTEMPT = 3
######################### split_file.py ########################################
BUOY_ID = {
    "300" : "MAMBO_2",
    "400" : "MAMBO_3",
    "500" : "MAMBO_4"
}
BUOY_DATA_DIR = "./boe/PC_Boe_Stazione_di_terra_runtime/"
BUOY_RT_DIR = "rt/"
BUOY_MSTAT_DIR = "mstat/"
BUOY_GPRMC_DIR = "gprmc/"
ADCP_DATA_DIR = "./correntometri_aquapro/rtdata/"
DEBUG_FOLDER_PFX = "_"
ARCHIVED_FILE_PFX = "_"
TMP_FILE_PFX = "."
SENT_FILE_PFX = "_"
DATA_FILE_EXT = ".txt"
