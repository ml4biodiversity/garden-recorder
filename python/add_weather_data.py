
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 10:09:00 2023

See LICENSE file in the root of the repository. 

Copyright (c) Aki Härmä, DACS/FSE, Maastricht University, 2023
"""

import pandas as pd
import numpy as np
import datetime as dt
import json
import requests
import os
from WeatherDataAccess import WeatherDataAccess


COLUMNS = ['datetime', 'lat', 'lon', 'solarRadiationHigh', 'uvHigh', 'winddirAvg',
          'humidityAvg', 'tempAve','windspeedAvg', 'windgustHigh', 
          'dewptAvg', 'pressureMax','precipRate']


def selected_measures(wudf):        
    wudf["datetime"] = wudf["obsTimeLocal"].apply(lambda x: dt.datetime.strptime(x ,"%Y-%m-%d %H:%M:%S"))
    wudf["tempAve"] = wudf["metric"].apply(lambda x: x["tempAvg"])
    # wudf["tempHigh"] = wudf["metric"].apply(lambda x: x["tempHigh"])
    # wudf["tempLow"] = wudf["metric"].apply(lambda x: x["tempLow"])    
    wudf["windspeedAvg"] = wudf["metric"].apply(lambda x: x["windspeedAvg"])
    wudf["windgustHigh"] = wudf["metric"].apply(lambda x: x["windgustHigh"])
    wudf["dewptAvg"] = wudf["metric"].apply(lambda x: x["dewptAvg"])
    wudf["pressureMax"] = wudf["metric"].apply(lambda x: x["pressureMax"])
    wudf["precipRate"] = wudf["metric"].apply(lambda x: x["precipRate"])
    return wudf[COLUMNS]


def turn_to_json(x):
    x = x.replace("er_path/", "") 
    try:
        out = json.loads(x.replace("\n","").replace("]","").replace("[","").replace('\'','"')[:-1]) 
    except:
        out = {}
    return (out)    


def add_weather_data(conf):
# Path where the data from Frontier device is stored (physical - not a link) 
    raw_data_path = conf["flpath"]   
    data_name = conf["data_name"] # Descriptive name this data set 
    number_of_frames = conf["number_of_frames_per_fragment"]  
    
    # Name of the data set
    ds = f'fl_{data_name}'
 
    file = f"./er_path/{ds}/{ds}.json"
    output_file = f"./er_path/{ds}/{ds}_metadata.xlsx"
    
    # Do not overwrite if the file exists
    if os.path.exists(output_file)==True:
        print("The metadata file exists - stopping.")
    
    with open(file,"r") as f:
        event_list = f.readlines()
        
    event_list = [turn_to_json(x) for x in event_list[1:-1]]    
    
    
    df = pd.DataFrame(event_list[1:-1])
    df = df.dropna(subset=["time"])
    df["wudate"] = df["time"].apply (lambda x: x[:11].replace("_","").split(".")[0])
    df["datetime"] = df["time"].apply (lambda x: dt.datetime.strptime(x.split(".")[0] ,"_%Y_%m_%d_%H_%M_%S"))
    cdf = df.copy()
    
    for c in COLUMNS[1:]:
        cdf.insert(len(df.columns),c,0.0)
    
    # Data dates
    wudates = cdf["wudate"].unique()
    
    # Search for a nearest weather station availabe on those days
    keys = json.load(open("Wunderground_ah_secret_keys.json","r"))
    WDA = WeatherDataAccess(keys["api_key"])
    wdata = WDA.find_station(conf, wudates)
    print(f"Found a station with all days of data: {wdata['stationName']} ({wdata['stationID']})")
    
    # Run for all unique days
    for wud in wudates:
        response = wdata["wdata"]["best"][wud]
        wudf = selected_measures(response)
        
        seldf = cdf[cdf["wudate"]==wud].index
        
        for s in seldf:
            nearest = np.argmin(abs(wudf["datetime"]-cdf.loc[s, "datetime"]))
            cdf.loc[s, COLUMNS[1:]] = wudf.loc[nearest,COLUMNS[1:]]
            
    cdf.to_excel(output_file)
        
    
