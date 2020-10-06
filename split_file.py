import os
import datetime
import time
import config

def new_file_in_dir(dir):
    '''Checks if there is more than one file in the raw dir to be processed.

    Params:
        dir(str): raw data files directory
    returns:
        True or False
    '''
    i = 0
    for file in os.listdir(dir):
        if file[0] not in [config.ARCHIVED_FILE_PFX, config.TMP_FILE_PFX]:
            i += 1
    if i > 1:
        return True
    return False

def buoy_gprmc_path(filepath):
    '''Creates buoy data file path according to current rules.

    Params:
        filepath(str): mamboX/yyyymmdd
    '''
    station = filepath.split("/")[0]  # mamboX
    file = filepath.split("/")[1]  # yyyymmdd
    id = {v.replace("_",""):k for k,v in config.BUOY_ID.items()}[station.upper()]
    new_file = "GPRMC_" + config.BUOY_ID[id] + "_" + file + config.DATA_FILE_EXT  # GPRMC_MAMBO_X_yyyymmdd.txt
    return (id + "_" + config.BUOY_ID[id] + "/" + config.BUOY_GPRMC_DIR + new_file)  # /xxx_MAMBO_X/gprmc/GPRMC_MAMBO_X_yyyymmdd.txt

def buoy_mstat_path(filepath):
    '''Creates buoy data file path according to current rules.

    Params:
        filepath(str): mamboX/yyyymmdd
    '''
    station = filepath.split("/")[0]  # mamboX
    file = filepath.split("/")[1]  # yyyymmdd
    id = {v.replace("_",""):k for k,v in config.BUOY_ID.items()}[station.upper()]
    new_file = "MSTAT_" + config.BUOY_ID[id] + "_" + file + config.DATA_FILE_EXT  # MSTAT_MAMBO_X_yyyymmdd.txt
    return (id + "_" + config.BUOY_ID[id] + "/" + config.BUOY_MSTAT_DIR + new_file)  # /xxx_MAMBO_X/mstat/MSTAT_MAMBO_X_yyyymmdd.txt

def buoy_data_path(filepath):
    '''Creates buoy data file path according to current rules.

    Params:
        filepath(str): mamboX/yyyymmdd
    '''
    station = filepath.split("/")[0]  # mamboX
    file = filepath.split("/")[1]  # yyyymmdd
    id = {v.replace("_",""):k for k,v in config.BUOY_ID.items()}[station.upper()]
    new_file = "Nmea_Data_ID_" + id + "_" + file + config.DATA_FILE_EXT  # Nmea_Data_ID_xxx_yyyymmdd.txt
    return (id + "_" + config.BUOY_ID[id] + "/" + config.DEBUG_FOLDER_PFX + config.BUOY_RT_DIR + new_file)  # /xxx_MAMBO_X/rt/Nmea_Data_ID_xxx_yyyymmdd.txt

def adcp_data_path(filepath):
    '''Creates adcp data file path according to current rules.

    Params:
        filepath(str): mamboX/yyyymmdd
    '''
    station = filepath.split("/")[0]  # mamboX
    file = filepath.split("/")[1]  # yyyymmdd
    id = {v.replace("_",""):k for k,v in config.BUOY_ID.items()}[station.upper()]
    new_file = "adcp_data_id" + id + "_mogs" + station[-1:] + "_" + file[0:4] + "_" + file[4:6] + "_" + file[6:8] + config.DATA_FILE_EXT  # adcp_data_idXXX_mogsX_yyyy_mm_dd.txt
    return (config.DEBUG_FOLDER_PFX + "mogs" + station[-1:] + "/" + new_file)  # /mogsX/adcp_data_idXXX_mogsX_yyyy_mm_dd.txt

def set_last_byte(tmp_file, pointer):
    '''Stores sent bytes counter into temp file.

    Params:
        tmp_file(str)
        pointer(int)
    '''
    with open(tmp_file, "w") as part:
        part.write(str(pointer))


def get_last_byte(tmp_file, stream):
    '''Gets sent bytes number from temp file.

    Params:
        tmp_file(str)
        stream(bytes)
    '''
    pointer = 0
    try:
        with open(tmp_file, "r") as part:
            pointer = int(part.read())
    except:
        pass
    stream.seek(pointer)

def main():
    '''Processes the raw files.'''
    # Iterates over buoy dir.
    for dir in os.listdir(config.BUOY_DATA_DIR + config.RAW_DIR):
        # Iterates over subdir.
        for file in os.listdir(config.BUOY_DATA_DIR + config.RAW_DIR + dir):
            buoy_data = []
            adcp_data = []
            mstat_data = []
            gprmc_data = []
            # Checks for unprocessed data files.
            if file[0] not in [config.ARCHIVED_FILE_PFX,config.TMP_FILE_PFX]:
                # Opens raw data file.
                with open(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/" + file, "r") as raw:
                    print("PROCESSING {} FILE {}".format(dir.upper(), file))
                    # Gets last processed byte from tmp file.
                    get_last_byte(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/" + config.TMP_FILE_PFX + file, raw)
                    # Reads raw file line by line.
                    #lines = raw.readlines()
                    #print(lines)
                    i=0
                    for line in raw:
                        ########################################################
                        if line[0:5] == "$ADCP":
                            #line = line.replace("$ADCP","$NORTEK")
                            line = line.replace(" ",",")  # Todo: remove at next firmware update.
                        # Marks down "METRECX" data as raw data "METRECXR"
                        #if line[0:8] == "$METRECX":
                        #    line = line.replace("$METRECX","$METRECXR")
                        ########################################################
                        print(line[:-1],end="\r")
                        # Splits lines to capture selected NMEA sentences.
                        line = line.split(",")
                        if line[0] in ["$YOUNG","$METRECXR"]:
                            # Formats data as string.
                            data = ",".join(line)  # "," separated list.
                            buoy_data.append(data)
                        if line[0] == "$MSTAT":
                            # Formats data as string, removes NMEA sentence tag.
                            data = ",".join(line)  # "," separated list.
                            mstat_data.append(data)
                        if line[0] == "$GPRMC":
                            # Formats data as string, removes NMEA sentence tag.
                            data = ",".join(line)  # "," separated list.
                            gprmc_data.append(data)
                        if line[0] == "$ADCP":
                            # Formats data as string, removes NMEA sentence tag.
                            data = ";".join(line[1:])  # ";" separated list.
                            adcp_data.append(data)
                        #time.sleep(0.005)
                        i+=1
                    print("{} {:" "<1000}".format(i,"LINES"))
                    pointer = raw.tell()  # Moves pointer to the end of file.
                    # Writes out last processed byte.
                    set_last_byte(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/"+ config.TMP_FILE_PFX + file, pointer)
                    # Writes out data to buoy file.
                    with open(config.BUOY_DATA_DIR + buoy_data_path(dir + "/" + file), "a") as data_file:
                        for row in buoy_data:
                            data_file.write(row)
                    # Writes out data to mstat file.
                    with open(config.BUOY_DATA_DIR + buoy_mstat_path(dir + "/" + file), "a") as mstat_file:
                        for row in mstat_data:
                            mstat_file.write(row)
                    # Writes out data to gprmc file.
                    with open(config.BUOY_DATA_DIR + buoy_gprmc_path(dir + "/" + file), "a") as gprmc_file:
                        for row in gprmc_data:
                            gprmc_file.write(row)
                    # Writes out data to adcp file.
                    with open(config.ADCP_DATA_DIR + adcp_data_path(dir + "/" + file), "a") as adcp_file:
                        for row in adcp_data:
                            adcp_file.write(row)
                # Checks if file has been completely processed and there is a newer file in raw dir.
                if pointer == os.stat(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/" + file)[6] and new_file_in_dir(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir):
                    # Marks down file as completely processed.
                    os.rename(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/" + file, config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/" + config.ARCHIVED_FILE_PFX + file)
                    # Deletes tmp file.
                    os.remove(config.BUOY_DATA_DIR + config.RAW_DIR + "/" + dir + "/" + config.TMP_FILE_PFX + file)
    return


if __name__ == "__main__":
    # Executes only if run as a script.
    main()
