#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 15 19:27:43 2025

@author: aki
"""

import os
import numpy as np
import pandas as pd
import torchaudio as ta
from time import sleep 

import jpype
# Enable Java imports
import jpype.imports

# Pull in types
from jpype.types import *

# Processing for data from Frontier Labs Bar LT recorders
def FrontierLabs_BLT_slice_to_fragments(conf):
    fl_path = conf["audio_path"]
    data_name = conf["data_name"] # Descriptive name this data set 
    number_of_frames = conf["number_of_frames_per_fragment"]  
    
    # Load meta data
    meta = pd.read_csv(f"{fl_path}Reclog.csv",skiprows=1)
    meta["time"] = meta["Date (DD/MM/YYYY)"]+meta["Time (HH:MM:SS)"]
    meta["time"] = pd.to_datetime(meta["time"], format="%d/%m/%Y %H:%M:%S ")

    # Setting up java access
    # os.environ['JAVA_HOME'] = '/home/aki/.jdks/openjdk-23.0.2/lib/server/'
    os.environ['JAVA_HOME'] = '/home/P70088732/jdk-24.0.2/lib/server/'
    # Launch the JVM (the jar should be moved here so that jype can see it)
    jpype.startJVM(classpath = ['./FieldAudioRecorder.jar'])
    
    jclass = jpype.JClass("FirstInFirstOut")()
    jclass.initialize(f'fl_{data_name}', number_of_frames)
    
    B = 12000
    stereo = False
    
    for c0 in range(meta.shape[0]):
        f = meta.loc[c0]
        afile = fl_path + f.Filename.split(":")[1]
        try:
            sig, fr = ta.load(afile)
        except:
            print(f"Reading file{afile} failed!!")
            continue
    
        if sig.shape[0]==2:
            stereo = True
        else: 
            stereo = False
            
        sig = sig*32000
        st = 0
        for c1 in range(np.int64(sig.shape[1]/B)):
            time = f["time"]+pd.Timedelta(seconds=st/48000)
            timestr = "_"+str(time).replace("-","_").replace(":","_").replace(" ","_")
            s = sig[:,st:(st+B)].double().numpy() 
            if stereo: 
                ja = JArray.of(np.r_[s[0:1,:],s[1:2,:]])
            else:
                ja = JArray.of(np.r_[s,s])
            jclass.write_float_array_to_buffer(ja, 2, timestr)
            # sleep(0.1)
            st += B
    
    jclass.close()
    jpype.shutdownJVM()
    
"""
    Main script for audio data preprocessing
"""
if __name__ == '__main__':
    pass
