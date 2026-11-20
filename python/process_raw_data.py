"""
@File  : process_raw_data.py
@Date  : 5/29/26  1:54 PM
@License: See license file is in the root of the repository.
@Desc  :

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""
import json
import sys
import preprocess_audio
import add_metadata

def main(local_conf):
    preprocess_audio.main(local_conf)
    add_metadata.main(local_conf)


if __name__ == '__main__':
    if sys.argv[1] is None:
        cfile = "conf.json"
    else:
        cfile = sys.argv[1]
    conf = json.load(open(cfile,"r"))
    print(f"Running {cfile}")
    main(conf)




