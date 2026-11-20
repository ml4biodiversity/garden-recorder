"""
@File  : process_all_aviaries.py
@Date  : 5/28/26  1:51 PM
@License: See license file is in the root of the repository.
@Desc  : Script for slicing and metadata processing for all raw Frontier Labs recordings.

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""

import json
import pandas as pd
import numpy as np
import queue
import threading
import subprocess
import os

# The queue for tasks
q = queue.Queue()

# Configuration template
conf = {"data_extraction_model":"frontier_labs",
 "audio_path":"",
 "data_name":"",
 "number_of_frames_per_fragment":12,
        "run_slicing": 1,
 "run_weather": 1,
 "run_speech_detection": 1,
 "run_speech_masking": 1
}

conf_path = "configs"

# Worker, handles each task
def worker():
    while True:
        item = q.get()
        if item is None:
            break
        print("Working on", item)
        conf_local = conf.copy()
        conf_local["data_name"] = item["preprocessed"][3:]
        conf_local["audio_path"] = item["raw data"] + "/"
        if item["run"]==0:
            print(f"Nothing to process in {conf_local['data_name']}")
            continue
        if item["run"]==1:
            print(f"Process only metadata in {conf_local['data_name']}")
            conf_local["run_slicing"] = 0
        if item["run"]==2:
            print(f"Preprocessing {conf_local['audio_path']} to {conf_local['data_name']}")

        conf_name = f"{conf_path}/conf_{str(threading.get_ident())}.json"
        json.dump(conf_local, open(conf_name, "w"))
        ret = subprocess.run(["python", "process_raw_data.py", conf_name])

        q.task_done()


def start_workers(worker_pool=6):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    return threads


def stop_workers(threads):
    # stop workers
    for i in threads:
        q.put(None)
    for t in threads:
        t.join()


def create_queue(task_items):
    for item in task_items:
        q.put(item)


if __name__ == "__main__":
    os.makedirs(conf_path, exist_ok=True)
    # Aviary data sets
    aviary_map = {"[storage0]":"/media/kakskyt/data/RawFrontier",
                  "[storage1]":"/media/aki/home/Data/FrontierLabs"}
    avia = pd.read_excel("aviary_data_maps.xlsx")
    avia["raw data"] = avia["raw data"].apply(lambda x: x.replace("[storage0]",
                                                                  aviary_map["[storage0]"]))
    avia["raw data"] = avia["raw data"].apply(lambda x: x.replace("[storage1]",
                                                                  aviary_map["[storage1]"]))
    avia = avia[avia["run"]==2].copy()
    avia = avia.T.to_dict()

    tasks = [avia[item] for item in avia]

    # Start up your workers
    workers = start_workers(worker_pool=4)
    create_queue(tasks)

    # Blocks until all tasks are complete
    q.join()

    stop_workers(workers)

