#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 08:50:11 2025

@author: aki
"""

import sys
import os
import json
from add_weather_data import add_weather_data
from process_speech_MITAST import process_all_data as mit_ast_speech_rejection

"""
    Main script for Frontier data preprocessing
"""
if __name__ == '__main__':
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
            add_weather_data(conf)
        except:
            print(f"{conf['data_name']} - failed")
            exit()
                    
    if conf["run_speech_detection"]==1:    
        print(f"Using MIT-AST to remove all speech in {conf['data_name']}")
        try:
            mit_ast_speech_rejection(conf)
        except:
            print(f"{conf['data_name']} - failed")
            exit()    

    if conf["run_birdnet"] == 1:
        print(f"Adding BirdNet data for {conf['data_name']}")
