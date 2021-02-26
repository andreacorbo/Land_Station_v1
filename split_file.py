# split_file.py
# MIT license; Copyright (c) 2020 - 2021 Andrea Corbo

import os
import datetime
import time
import cfg

# Checks if there is more than one file in the raw dir to be processed.
def new_file_in_dir(dir):
    i = 0
    for file in os.listdir(dir):
        try:
             int(file)
             i += 1
        except ValueError:
            continue
    if i > 1:
        return True
    return False

# Creates buoy data file path according to current rules.
def buoy_gprmc_path(filepath):
    # filepath: mamboX/yyyymmdd
    station = filepath.split('/')[0]  # mamboX
    file = filepath.split('/')[1]  # yyyymmdd
    id = {v.replace('_',''):k for k,v in cfg.BUOY_ID.items()}[station.upper()]
    new_file = 'GPRMC_' + cfg.BUOY_ID[id] + '_' + file + cfg.DATA_FILE_EXT  # GPRMC_MAMBO_X_yyyymmdd.txt
    return (id + '_' + cfg.BUOY_ID[id] + '/' + cfg.BUOY_GPRMC_DIR + new_file)  # /xxx_MAMBO_X/gprmc/GPRMC_MAMBO_X_yyyymmdd.txt

# Creates buoy data file path according to current rules.
def buoy_mstat_path(filepath):
    # filepath: mamboX/yyyymmdd
    station = filepath.split('/')[0]  # mamboX
    file = filepath.split('/')[1]  # yyyymmdd
    id = {v.replace('_',''):k for k,v in cfg.BUOY_ID.items()}[station.upper()]
    new_file = 'MSTAT_' + cfg.BUOY_ID[id] + '_' + file + cfg.DATA_FILE_EXT  # MSTAT_MAMBO_X_yyyymmdd.txt
    return (id + '_' + cfg.BUOY_ID[id] + '/' + cfg.BUOY_MSTAT_DIR + new_file)  # /xxx_MAMBO_X/mstat/MSTAT_MAMBO_X_yyyymmdd.txt

# Creates buoy data file path according to current rules.
def buoy_data_path(filepath):
    # filepath: mamboX/yyyymmdd
    station = filepath.split('/')[0]  # mamboX
    file = filepath.split('/')[1]  # yyyymmdd
    id = {v.replace('_',''):k for k,v in cfg.BUOY_ID.items()}[station.upper()]
    new_file = 'Nmea_Data_ID_' + id + '_' + file + cfg.DATA_FILE_EXT  # Nmea_Data_ID_xxx_yyyymmdd.txt
    return (id + '_' + cfg.BUOY_ID[id] + '/' + cfg.DEBUG_FOLDER_PFX + cfg.BUOY_RT_DIR + new_file)  # /xxx_MAMBO_X/rt/Nmea_Data_ID_xxx_yyyymmdd.txt

# Creates adcp data file path according to current rules.
def adcp_data_path(filepath):
    # filepath: mamboX/yyyymmdd
    station = filepath.split('/')[0]  # mamboX
    file = filepath.split('/')[1]  # yyyymmdd
    id = {v.replace('_',''):k for k,v in cfg.BUOY_ID.items()}[station.upper()]
    new_file = 'adcp_data_id' + id + '_mogs' + station[-1:] + '_' + file[0:4] + '_' + file[4:6] + '_' + file[6:8] + cfg.DATA_FILE_EXT  # adcp_data_idXXX_mogsX_yyyy_mm_dd.txt
    return (cfg.DEBUG_FOLDER_PFX + 'mogs' + station[-1:] + '/' + new_file)  # /mogsX/adcp_data_idXXX_mogsX_yyyy_mm_dd.txt

# Creates buoy data file path according to current rules.
def garbage_data_path(filepath):
    # filepath: mamboX/yyyymmdd
    station = filepath.split('/')[0]  # mamboX
    file = filepath.split('/')[1]  # yyyymmdd
    id = {v.replace('_',''):k for k,v in cfg.BUOY_ID.items()}[station.upper()]
    new_file = file + cfg.DATA_FILE_EXT  # yyyymmdd.txt
    return (id + '_' + cfg.BUOY_ID[id] + '/' + cfg.GARBAGE_DATA_DIR + new_file)  # /xxx_MAMBO_X/garbage/yyyymmdd.txt


# Stores sent bytes counter into temp file.
def set_last_byte(tmp_file, pointer):
    with open(tmp_file, 'w') as part:
        part.write(str(pointer))


# Gets sent bytes number from temp file.
def get_last_byte(tmp_file, stream):
    pointer = 0
    try:
        with open(tmp_file, 'r') as part:
            pointer = int(part.read())
    except:
        pass
    stream.seek(pointer)

def reformat_date(iso8601):
    # Re-formats controller timestamp according to NODC specs.
    # yyyy-mm-ddThh:mm:ssZ -> mmddyy,hhmmss
    ts = iso8601.split('T')
    dt = ts[0].split('-')
    dt = '{}{}{}'.format(dt[1],dt[2],dt[0][2:])
    tm = ts[1][:-1].split(':')
    tm = '{}{}{}'.format(tm[0],tm[1],tm[2])
    return '{},{}'.format(dt,tm)

# Processes the raw files.
def main():
    print('PROCESSING FILES...')
    # Iterates over buoy dir.
    for dir in os.listdir(cfg.BUOY_DATA_DIR + cfg.RAW_DIR):
        # Iterates over subdir.
        for file in os.listdir(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + dir):
            buoy_data = []
            adcp_data = []
            mstat_data = []
            gprmc_data = []
            garbage_data = []
            # Checks for unprocessed data files.
            #if file[0] not in [cfg.ARCHIVED_FILE_PFX,cfg.TMP_FILE_PFX] and not os.path.isdir(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/' + file):
            try:
                int(file)
                # Opens raw data file.
                with open(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + dir + '/' + file, 'r') as raw:
                    print('PROCESSING {} FILE {}'.format(dir.upper(), file))
                    # Gets last processed byte from tmp file.
                    get_last_byte(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/' + cfg.TMP_FILE_PFX + file, raw)
                    # Reads raw file line by line.
                    #lines = raw.readlines()
                    #print(lines)
                    i=0
                    for l in raw:
                        line = l.lstrip('\x1a')  # Removes missed pad bytes.
                        print(line[:-1],end='\r')
                        line = line.split(',')
                        # Splits lines to capture selected NMEA sentences.
                        if line[0] == '$YOUNG':
                            if len(line) == 14:
                                line[0] = '$METEO'  # To be compliant with old rules.
                                line[2] = reformat_date(line[2])  # To be compliant with old rules.
                                data = ','.join(line)  # ',' separated list.
                                buoy_data.append(data)
                            else:
                                garbage_data.append(data)
                        if line[0] == '$METRECXR':
                            if len(line) == 16:
                                line[2] = reformat_date(line[2])  # To be compliant with old rules.
                                data = ','.join(line)  # ',' separated list.
                                buoy_data.append(data)
                            else:
                                garbage_data.append(data)
                        if line[0] == '$MSTAT':
                            if len(line) == 11:
                                line[2] = reformat_date(line[2])  # To be compliant with old rules.
                                data = ','.join(line)  # ',' separated list.
                                mstat_data.append(data)
                            else:
                                garbage_data.append(data)
                        if line[0] == '$GPRMC':
                            if len(line) == 13:
                                data = ','.join(line)  # ',' separated list.
                                gprmc_data.append(data)
                            else:
                                garbage_data.append(data)
                        if line[0] == '$NORTEK':
                            if len(line) == 99:
                                line[2] = reformat_date(line[2])  # To be compliant with old rules.
                                # Formats data as string, removes NMEA sentence tag.
                                data = ';'.join(line[3:])  # ';' separated list.
                                adcp_data.append(data)
                            else:
                                garbage_data.append(data)
                        #time.sleep(0.005)
                        i+=1
                    print('{} {:' '<1000}'.format(i,'LINES'))
                    pointer = raw.tell()  # Moves pointer to the end of file.
                    # Writes out last processed byte.
                    set_last_byte(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/'+ cfg.TMP_FILE_PFX + file, pointer)
                    # Writes out data to buoy file.
                    with open(cfg.BUOY_DATA_DIR + buoy_data_path(dir + '/' + file), 'a') as data_file:
                        for row in buoy_data:
                            data_file.write(row)
                    # Writes out data to mstat file.
                    with open(cfg.BUOY_DATA_DIR + buoy_mstat_path(dir + '/' + file), 'a') as mstat_file:
                        for row in mstat_data:
                            mstat_file.write(row)
                    # Writes out data to gprmc file.
                    with open(cfg.BUOY_DATA_DIR + buoy_gprmc_path(dir + '/' + file), 'a') as gprmc_file:
                        for row in gprmc_data:
                            gprmc_file.write(row)
                    # Writes out data to adcp file.
                    with open(cfg.ADCP_DATA_DIR + adcp_data_path(dir + '/' + file), 'a') as adcp_file:
                        for row in adcp_data:
                            adcp_file.write(row)
                # Writes out data to garbage file.
                with open(cfg.BUOY_DATA_DIR + garbage_data_path(dir + '/' + file), 'a') as garbage_file:
                    for row in garbage_data:
                        garbage_file.write(row)
            # Checks if file has been completely processed and there is a newer file in raw dir.
                if pointer == os.stat(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/' + file)[6] and new_file_in_dir(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir):
                    try:
                        # Marks down file as completely processed.
                        os.rename(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/' + file, cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/' + cfg.ARCHIVED_FILE_PFX + file)
                    except Exception as err:
                        print(err)
                    try:
                        # Deletes tmp file.
                        os.remove(cfg.BUOY_DATA_DIR + cfg.RAW_DIR + '/' + dir + '/' + cfg.TMP_FILE_PFX + file)
                    except Exception as err:
                        print(err)
            except ValueError:
                continue

if __name__ == '__main__':
    # Executes only if run as a script.
    main()
