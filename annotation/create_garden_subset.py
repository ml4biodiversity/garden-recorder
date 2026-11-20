"""
@File  : create_garden_subset.py.py
@Date  : 5/29/26  6:58 PM
@License: See license file is in the root of the repository.
@Desc  :

Copyright (c) Aki Härmä, DACS, Maastricht University, 2026.
"""

import pandas as pd

dat = pd.read_excel("er_path/metadata.xlsx")

cols = ['filename', 'MIT_AST_label', 'target_species', 'id',
       'target_confidence']

out = dat['filename', 'MIT_AST_label'].copy()


if __name__ == '__main__':
    pass
