"""
@File  : plot_detections.py
@Date  : 4/3/202611:03 AM
@License: See license file is in the root of the repository.
@Desc  : A script to visualize some of the recorded data

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""

import pandas as pd
import json
import seaborn as sns

file = "visualization/fl_vuurpad_march2026_data_metadata_speechless_birds.xlsx"

data = pd.read_excel(file, index_col=0)

"""
    Select top bird or the mit-ast detection
"""
def get_top_bird(item):
    try:
        return json.loads(item["Birdnet_detections"].replace("'","\""))[0]["common_name"]
    except:
        return "No Bird" #item["MIT_AST_label"]


data["detection"] = data.apply(lambda x: get_top_bird(x), axis=1)

select = ["European Robin","Great Tit", "Eurasian Blackbird","Tawny Owl","Eurasian Blue Tit","Eurasian Jay",
          "Common Chiffchaff","Common Buzzard","Common Raven",'Common Chiffchaff','Great Spotted Woodpecker']

seldata = data[data["detection"].apply(lambda x: x in select)]

sns.scatterplot(data=seldata, x="datetime", y="detection", hue="detection")

if __name__ == '__main__':
    pass
