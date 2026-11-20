#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 08:50:11 2025

@author: aki
"""
import pandas as pd
import sys
import os
import json
from add_weather_data import add_weather_data, add_weather_data_garden
from process_speech_MITAST import process_all_data as mit_ast_speech_rejection
from process_speech_masking import process_all_data as speech_masking

"""
    Main script for Frontier data preprocessing
"""
def main(conf=None):
    if type(conf) is not dict:
        if len(sys.argv)<2:
            print("No configuration file - defaulting to conf.json")
            cfile = "conf.json"
        else:
            cfile = sys.argv[1]
        if not os.path.exists(cfile):
            print("No configuration available - exiting")
            exit(-1)

        conf = json.load(open(cfile, "r"))

    if conf["run_weather"]==1:            
        print(f"Adding weather data for {conf['data_name']}")
        try:
            if conf["data_extraction_model"] == "frontier_labs":
                gps = pd.read_csv(f"{conf["audio_path"]}/GPS_log.csv", skiprows=1)
                conf["latitude"] = str(gps.loc[0, 'Latitude (decimal degrees)'])
                conf["longitude"] = str(gps.loc[0, 'Longitude (decimal degrees)'])
                add_weather_data(conf)
            if conf["data_extraction_model"] == "audiomoth":
                add_weather_data(conf)
            if conf["data_extraction_model"] == "garden":
                add_weather_data_garden(conf)

        except:
            print(f"Adding weather data to {conf['data_name']} failed")
            exit()
                    
    if conf["run_speech_detection"]==1:    
        print(f"Using MIT-AST to classify sound events in {conf['data_name']}")
        try:
            mit_ast_speech_rejection(conf)
        except:
            print(f"MIT-AST processing of {conf['data_name']} - failed")
            exit()

    if conf["run_speech_masking"] == 1:
        print(f"Running Silero VAD speech masking for {conf['data_name']}")
        try:
            speech_masking(conf)
        except:
            print(f"Silero processing {conf['data_name']} - failed")
            exit()

if __name__ == '__main__':
    main()