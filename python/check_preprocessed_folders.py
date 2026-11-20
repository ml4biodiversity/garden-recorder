"""
@File  : check_preprocessed_folders.py
@Date  : 6/3/26  8:08 AM
@License: See license file is in the root of the repository.
@Desc  :

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""

import pandas as pd
import os
from pathlib import Path

column_set = {'sessionId', 'time', 'filename', 'th1', 'th1_value', 'th2',
              'th2_value', 'th3', 'th3_value', 'wudate', 'datetime',
              'precipRate', 'pressureMax', 'dewptAvg', 'windgustHigh',
              'windspeedAvg', 'tempAve', 'humidityAvg', 'winddirAvg',
              'uvHigh', 'solarRadiationHigh', 'lon', 'lat', 'MIT_AST_label',
              'speech_masked_pct', 'speech_masked_intervals'}


if __name__ == '__main__':
    apath = "/media/kakskyt/data/zoodata/er_path/"
    avia = pd.read_excel("aviary_data_maps.xlsx")

    for c1 in range(avia.shape[0]):
        item = avia.loc[c1]
        metafile = f"{apath}{item['preprocessed']}/{item['preprocessed']}_metadata.xlsx"
        avia.loc[c1,"meta_exists"] = os.path.exists(metafile)*1
        if avia.loc[c1,"meta_exists"]:
            meta = pd.read_excel(metafile, index_col=0)
            avia.loc[c1,"missing_columns"] = str(set(meta.columns)
                                                 -column_set-{'Unnamed: 0', 'Unnamed: 0.1'})
            avia.loc[c1,"start_time"] = meta.loc[0,"datetime"]
            avia.loc[c1, "end_time"] = meta.iloc[-1]["datetime"]
            avia.loc[c1, "duration"] = str(avia.loc[c1, "end_time"] - avia.loc[c1, "start_time"])
            avia.loc[c1, "total_rows"] = meta.shape[0]
            avia.loc[c1, "masked_speech_rows"] = sum(meta["speech_masked_pct"]>0.0)
            datapath = f"{apath}{item['preprocessed']}"
            avia.loc[c1, "audio_files"] =len(list(Path(datapath).rglob("*.wav")))

        avia.to_excel("aviary_data_maps_validation_results.xlsx")