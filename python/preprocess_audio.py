#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 08:50:11 2025

@author: aki
"""

import sys
import os
import json
from specific_data_converters import FrontierLabs_BLT_slice_to_fragments

"""
    Main script for audio data preprocessing
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
    
    if conf["data_extraction_model"]=="frontier_labs":
        print(f"Running segmentation for {conf['data_name']} using {conf['data_extraction_model']}")
        try:
            FrontierLabs_BLT_slice_to_fragments(conf)
        except:
            print(f"{conf['data_name']} - failed")
            exit()

            
    # to add species detection
