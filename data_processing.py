buoyId = {
    "300" : "MAMBO_2",
    "400" : "MAMBO_3",
    "500" : "MAMBO_4"
}    

def set_path(self, filepath):
    station = filepath.split("/")[0]
    file = filepath.split("/")[1]
    id = {v.replace("_",""):k for k,v in self.buoyId.items()}[station.upper()]
    new_file = "Nmea_Data_ID_" + id + "_" + file + ".txt"
    return ("/" + id + "_" + self.buoyId[id] + "/data/" + new_file)
