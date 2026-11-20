import pandas as pd
file1 = "/media/kakskyt/data/RawFrontier/ZooAachen/balistarling_may2026/Reclog.csv"
file2 = "/media/kakskyt/data/RawFrontier/ZooAachen/Ibises_may2026/Reclog.csv"
df1 = pd.read_csv(file1, skiprows=1)
df2 = pd.read_csv(file2, skiprows=1)

targetdf = df1.copy()

Ndf2 = df2.shape[0]
for c1 in range(targetdf.shape[0]):
    if c1<Ndf2-1:
        targetdf.loc[c1,'Date (DD/MM/YYYY)']=df2.loc[c1,'Date (DD/MM/YYYY)']
    else:
        if c1<131:
            targetdf.loc[c1, 'Date (DD/MM/YYYY)'] = '11/05/2026 '
        else:
            targetdf.loc[c1, 'Date (DD/MM/YYYY)'] = '12/05/2026 '

targetdf.to_csv("/media/kakskyt/data/RawFrontier/ZooAachen/balistarling_may2026/Reclog.csv")
