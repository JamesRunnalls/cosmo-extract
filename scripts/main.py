import os
from time import mktime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import netCDF4
from datetime import datetime, timedelta, date


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


folder = "../data/COSMO1"
out_folder = "../data/output"
files = os.listdir(folder)
files.sort()
points = {
    "Inkwilersee": [47.197, 7.674],
    "Geistsee": [46.763, 7.533],
    "Lenkerseeli": [46.451, 7.445],
    "Stockseewli": [46.598, 8.326],
    "Meiefallseeli": [46.584, 7.584],
    "Oberes Banzlauiseeli": [46.687, 8.280],
    "Atzenholzerweiher": [47.498, 9.334],
    "Bildweiher": [47.408, 9.305],
    "Eselschwanzweiher": [47.469, 9.615],
    "Grappelensee": [47.208, 9.279],
    "Stadtweiher Wil": [47.466, 9.053],
    "Voralpsee": [47.158, 9.382],
    "Lake Sempach": [47.145, 8.162],
    "Agerisee": [47.122, 8.618],
    "Lake Sarnen": [46.866, 8.215],
    "Lake Murten": [46.933, 7.085],
}
params = ["time", "T_2M", "U", "V", "GLOB", "RELHUM_2M", "TOT_PREC", "LW_IN_TG"]
output = {}
for key, value in points.items():
    output[key] = {}
    for p in params:
        output[key][p] = []

start_date = date(2017, 1, 1)
end_date = date(2022, 1, 1)
for d in daterange(start_date, end_date):
    # file = r"M:\COSMO1\{}\cosmo2_epfl_lakes_{}.nc".format(d.strftime("%Y"), d.strftime("%Y%m%d"))
    file = r"/home/jamesrunnalls/git/cosmo_extract/data/COSMO1/{}/cosmo2_epfl_lakes_{}.nc".format(d.strftime("%Y"),
                                                                                                  d.strftime("%Y%m%d"))
    if not os.path.exists(file):
        print("Cannot find file: {}".format(file))
        continue

    nc = netCDF4.Dataset(os.path.join(folder, file), mode='r', format='NETCDF4_CLASSIC')
    lat = np.array(nc.variables["lat_1"])
    lon = np.array(nc.variables["lon_1"])

    timeunits = nc.variables["time"].units.split(" ")
    starttime = datetime.strptime(timeunits[-2] + timeunits[-1], "%Y-%m-%d%H:%M:%S")
    time = np.array(nc.variables["time"])
    time = np.array([starttime + timedelta(hours=t) for t in time])
    time = np.array([mktime(t.timetuple()) for t in time])

    for key, value in points.items():
        diff = ((lat - value[0]) ** 2 + (lon - value[1]) ** 2) ** 0.5
        loc = np.argwhere(diff == np.min(diff))[0]
        output[key]["time"] = output[key]["time"] + list(time)
        for p in params:
            if p != "time":
                if len(nc.variables[p].dimensions) == 3:
                    data = nc.variables[p][:, loc[0], loc[1]]
                elif len(nc.variables[p].dimensions) == 4:
                    data = nc.variables[p][:, 0, loc[0], loc[1]]
                if p == "T_2M":
                    data = data - 273.15
                output[key][p] = output[key][p] + list(data)
    nc.close()

for key, value in output.items():
    df = pd.DataFrame.from_dict(value)
    df.to_csv(os.path.join(out_folder, "_".join([key, str(points[key][0]), str(points[key][1])]) + ".csv"), index=False)