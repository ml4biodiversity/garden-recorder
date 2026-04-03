#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 09:38:39 2025

@author: aki
"""

import pandas as pd
import numpy as np
import datetime as dt
import json
import requests
import os


class WeatherDataAccess():
    def __init__(self, api_key):
        self.keys = {"site":"https://www.wunderground.com/",
        "api_key":f"{api_key}",
        "path":"http://api.wunderground.com/api/"}
        self.stationId = None
        self.stationName = None
        
        
    def get_complete_weather_data(self, resp, wudates):    
        xx = self
        N = len(resp["location"]["stationName"])
        station = None
        weathers = {}
        for c1 in range(N):
            stid = resp["location"]["stationId"][c1]
            daycount = 0
            weathers[stid] = {}
            for wd in wudates:
                response = xx.get_dated_data(wd, STATION=stid)
                if response.shape[0]>0:
                    daycount+=1                               
                    weathers[stid][wd] = response
            # Found a full series!
            if (daycount==len(wudates)) & (resp["location"]["qcStatus"][c1]==1):
                station = c1                
                weathers["best"] = weathers[stid] 
                break
        return weathers, station        
    

    def find_station(self, conf, wudates, location=None):
        API_KEY = self.keys['api_key']

        lat = conf["latitude"]
        lon = conf["longitude"]

        url = ["https://api.weather.com/v3/location/near?",
               f"geocode={lat},{lon}&product=pws&",
               f"format=json&apiKey={API_KEY}"]
        response = requests.get("".join(url)).json()

        # Fist station where qcstatus==1 and dates available
        wdata, sid = self.get_complete_weather_data(response, wudates)
        if sid == None:
            print("No stations found!! Exiting.")
            return

       	self.stationId = response["location"]["stationId"][sid]
        self.stationName = response["location"]["stationName"][sid]
        return {"stationID":self.stationId, "stationName":self.stationName, 
                "wdata":wdata}
    
    
    def get_dated_data(self, wud, STATION=None):
        if STATION==None:            
            STATION = self.stationId 
        API_KEY = self.keys['api_key']
        url = ["https://api.weather.com/v2/pws/history/all",
                f"?stationId={STATION}&format=json&units=m&",
                f"date={wud}&apiKey={API_KEY}&numericPrecision=decimal"]
        response = requests.get("".join(url)).json()
        wudf = pd.DataFrame(response["observations"])
        return wudf
    
    
    

"""
    Test
"""
if __name__ == '__main__':
    WDA = WeatherDataAccess()
    lat = 51.459
    lon = 5.598
    
    place = WDA.find_station(None, [lat, lon])
    print(place)
    
    data = WDA.get_dated_data("20250817")
    print(data)
    
    
        
    