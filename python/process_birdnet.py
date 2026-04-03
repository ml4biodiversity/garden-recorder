#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 15:22:37 2024

See LICENSE file in the root of the repository. 

Copyright (c) Aki Härmä, DACS/FSE, Maastricht University, 2023
"""

import os
from pathlib import Path
import datetime as dt
import pandas as pd
import torch
import json
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

class BirdnetClass():
    def __init__(self, conf):
    # Load and initialize the BirdNET-Analyzer models.
        # self.analyzer = Analyzer(custom_species_list="zoodata/selected_species.txt")
        self.analyzer = Analyzer()
        self.conf = conf
        self.date = dt.datetime.strptime(conf["start_time"],"%d-%m-%Y %H:%M:%S")
        self.min_conf = 0.002
    def process(self, afile, meta):
        recording = Recording(
            self.analyzer,
            afile,
            lat=self.conf["latitude"],
            lon=self.conf["longitude"],
            date=self.date, # use date or week_48
            min_conf=0.00025,
        )
        recording.analyze()
        return str(recording.detections)


def process_all_data(conf):

    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    fpath = f"./er_path/fl_{conf['data_name']}"
    fpath0 = "./er_path/"
    all_files = list(Path(fpath).rglob("*_speechless.xlsx"))

    BC = BirdnetClass(conf)

    for mfile in all_files:
        mfile = str(mfile)
        print(f"MIT processing {mfile}")
        data = pd.read_excel(mfile,index_col=0)
        data = data.dropna(subset=["time"])
        data["Birdnet_detections"] = ""

        for c1 in range(data.shape[0]):
            try:
                afile = fpath0+data.loc[c1, "filename"]
                data.loc[c1, "Birdnet_detections"] = BC.process(afile, conf)
            except:
                data.loc[c1, "Birdnet_detections"] = "failed"

        newfile = mfile[:-5] + "_birds.xlsx"
        data.to_excel(newfile)


if __name__ == '__main__':
    conf = json.load(open("conf.json", "r"))
    process_all_data(conf)


