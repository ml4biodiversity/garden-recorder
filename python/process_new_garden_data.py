"""
@File  : process_raw_data.py
@Date  : 5/29/26  1:54 PM
@License: See license file is in the root of the repository.
@Desc  :

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""
import json
import os
import add_metadata
from add_weather_data import add_weather_data_garden
from process_speech_MITAST import process_all_data_garden
from pathlib import Path


def main():
    cfile = "conf_garden.json"
    conf = json.load(open(cfile,"r"))

    # Select folders that have no excel files
    p = Path(conf["audio_path"]+"/")
    pnames = [x for x in p.iterdir() if x.is_dir()]
    pnames = [p for p in pnames if not any(list(p.glob("*.xlsx")))]

    for p in pnames:
        print(p)
        conf["data_name"] = p.parts[-1]
        conf["audio_path"] = str(p)
        if conf["run_weather"]==1:
            add_weather_data_garden(conf)

        if conf["run_speech_detection"]==1:
            process_all_data_garden(conf)



if __name__ == '__main__':
    main()