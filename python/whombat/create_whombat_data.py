"""
@File  : create_whombat_data.py.py
@Date  : 4/7/202610:27 AM
@License: See license file is in the root of the repository.
@Desc  :

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""


import pandas as pd
import os
import soundfile

def main():
    metafiles = ["garden_20260221/garden_20260221_metadata.xlsx"]
    metafile = metafiles[0]
    meta = pd.read_excel(metafile)
    outpath = "test_wb"
    os.makedirs(outpath, exist_ok=True)
    # Number of files
    N = 1000
    selected = meta.sample(N, replace=False).reset_index(drop=True)

    for c1 in range(N):
        fname = meta.loc[c1, "filename"]
        src = selected.loc[1, "filename"][8:]
        sig,f = soundfile.read(src)
        dst = f"{outpath}/{fname.split("/")[-1]}"
        soundfile.write(dst, sig[:,0], f)
    selected.to_excel(f"{outpath}/metadata.xlsx", index=False)


if __name__ == '__main__':
    main()

