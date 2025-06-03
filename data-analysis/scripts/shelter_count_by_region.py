"""
this script is suppose to be run in google colab
"""

import os

import pandas as pd

data_ws = (
    "/content/drive/MyDrive/2025 雙北黑客松/data/防災應變-旅遊景點周圍防災設施分析/"
)
assert "readme.md" in os.listdir(data_ws)
os.chdir(data_ws)

df = pd.read_csv(data_ws + "clean/合併/" + "避難收容處所合併.csv")
to_exclude = [
    "收容所編號",
    "名稱",
    "門牌地址",
    "類型",
    "聯絡人姓名",
    "聯絡人連絡電話",
    "管理人姓名",
    "管理人連絡電話",
    "備考",
    "完整地址",
    "服務里別",
]
df.drop(columns=to_exclude, inplace=True)
# df.head()

# 1. 定義災別欄位
disaster_cols = ["水災", "震災", "土石流", "海嘯"]

# 2. 將「Y」或「是」視為 True，其餘視為 False，並存到新欄位 (col + "_bool")
for col in disaster_cols:
    df[col + "_bool"] = df[col].isin(["Y", "是"])

# 3. 針對「鄉鎮」分組，把各災別的布林 (True/False) 做 sum()
#    因為 True 當作 1、False 當作 0，sum() 就能得到「該鄉鎮底下，有多少個地點可以對應該災別」
grouped = (
    df.groupby(["縣市", "鄉鎮"])[[col + "_bool" for col in disaster_cols]]
    .sum()
    .reset_index()
)

# 4. 重命名欄位為較易閱讀的名稱
grouped = grouped.rename(
    columns={
        "水災_bool": "flood_shelter_count",
        "震災_bool": "earthquake_shelter_count",
        "土石流_bool": "landslide_shelter_count",
        "海嘯_bool": "tsunami_shelter_count",
        "縣市": "city",
    }
)

# 5. （選項）如果要計算「該地點至少支援一種災別」的總數，可以再額外做：
#    先為每一列新增「任一災別」欄：只要該列任一災別欄位是 "Y" 或 "是"，就算 True
df["任一災別"] = df[disaster_cols].apply(
    lambda row: row.isin(["Y", "是"]).any(), axis=1
)

#    再按「鄉鎮」分組加總
total_any = (
    df.groupby("鄉鎮")["任一災別"]
    .sum()
    .reset_index()
    .rename(columns={"任一災別": "任一災別避難地點數"})
)

# 6. 合併「各災別避難地點數」與「任一災別避難地點數」
result = pd.merge(grouped, total_any, on="鄉鎮", how="left")

# result.head()

# 儲存雙北結果
result.to_csv(data_ws + "component_ready/" + "disaster.csv", index=False)

# 儲存臺北市結果
result_tp = result[result["city"] == "臺北市"]
result_tp.to_csv(data_ws + "component_ready/" + "disaster_tp.csv", index=False)
