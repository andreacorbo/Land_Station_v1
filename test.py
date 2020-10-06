import os
import config

def files_to_send():

    for root, subdirs, files in os.walk(config.SOFTWARE_DIR):
        for file in files:
            if file[0] not in (config.TMP_FILE_PFX, config.SENT_FILE_PFX):
                yield os.path.join(root, file)
    if any (files for root, subdirs, files in os.walk(config.SOFTWARE_DIR)):
        yield "\x00"

if files_to_send():
    print("gotcha")
