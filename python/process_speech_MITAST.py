#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 15:22:37 2024

See LICENSE file in the root of the repository. 

Copyright (c) Aki Härmä, DACS/FSE, Maastricht University, 2025
"""

import os
import torch
from pathlib import Path
import pandas as pd
from mit_model_call import MIT_AST_model
import json

def process_all_data(conf):        
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    fpath = f"./er_path/fl_{conf['data_name']}"
    fpath0 = "./er_path/"
    all_files = list(Path(fpath).rglob("*_metadata.xlsx"))

    classifier = MIT_AST_model()
    classifier.model.to(DEVICE)
        
    for mfile in all_files:
        mfile = str(mfile)
        print(f"MIT processing {mfile}")        
        data = pd.read_excel(mfile)    
        data = data.dropna(subset=["time"])
        data["MIT_AST_label"] = ""    

                       
        for c1 in range(data.shape[0]):           
            try:
                afile = fpath0+data.loc[c1, "filename"]
                data.loc[c1, "MIT_AST_label"] = classifier.classify(afile)
            except: 
                data.loc[c1, "MIT_AST_label"] = "file_missing"
                continue
            if data.loc[c1, "MIT_AST_label"]=="Speech":
                data.loc[c1, "MIT_AST_label"] = "speech_removed"
                if os.path.isfile(afile):
                    os.remove(afile)
        newfile = mfile[:-5]+"_speechless.xlsx"
        data.to_excel(newfile)
    
        
if __name__ == '__main__':
    conf = json.load(open("conf.json", "r"))
    process_all_data(conf)
    
