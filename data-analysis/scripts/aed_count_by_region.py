"""
this script is suppose to be run in google colab
"""

import os

import geopandas as gpd
import pandas as pd
from pyproj import CRS, Transformer
from shapely.geometry import Point

data_ws = (
    "/content/drive/MyDrive/2025 雙北黑客松/data/防災應變-旅遊景點周圍防災設施分析/"
)
assert "readme.md" in os.listdir(data_ws)
os.chdir(data_ws)

aed = pd.read_csv(data_ws + "clean/合併/" + "AED_list.csv")
# aed.head()

population = pd.read_csv(data_ws + "clean/合併/" + "merged_population.csv")
population = population.sort_values("鄉鎮市區名稱")
# population.head()

# Convert '資料時間' to a comparable format
population["資料時間_year"] = population["資料時間"].str.extract(r"(\d+)Y").astype(int)

# Find the latest year for each location
latest_year_per_location = (
    population.groupby("鄉鎮市區名稱")["資料時間_year"].max().reset_index()
)

# Merge to get the rows corresponding to the latest year for each location
population_latest_year = pd.merge(
    population,
    latest_year_per_location,
    on=["鄉鎮市區名稱", "資料時間_year"],
    how="inner",
)
population = population_latest_year.sort_values("鄉鎮市區名稱")

# population.head()

aed_count_by_region = (
    aed.groupby(["場所縣市", "場所區域"])["場所名稱"]
    .count()
    .reset_index(name="aed_count")
)
# aed_count_by_region.head()

# 儲存雙北結果
aed_count_by_region.to_csv(
    data_ws + "component_ready/" + "aed_count_by_region.csv", index=False
)

# 儲存臺北市結果
aed_count_by_region_tp = aed_count_by_region[
    aed_count_by_region["場所縣市"] == "臺北市"
]
aed_count_by_region_tp.to_csv(
    data_ws + "component_ready/" + "aed_count_by_region_tp.csv", index=False
)

merged_df = pd.merge(
    aed_count_by_region,
    population,
    left_on=["場所縣市", "場所區域"],
    right_on=["縣市名稱", "鄉鎮市區名稱"],
    how="left",
)
# merged_df['aed_per_capita'] = merged_df['aed_count'] / merged_df['人口數']
# merged_df.fillna(0, inplace=True) # Handle potential missing values by filling with 0
# merged_df.head()

merged_df["people_per_aed"] = merged_df["人口數"] / merged_df["aed_count"]
merged_df.fillna(
    0, inplace=True
)  # Handle potential missing values (regions with 0 AEDs)
# merged_df.head()

spatial_dispersion_df = (
    aed.groupby(["場所縣市", "場所區域"])[["地點LAT", "地點LNG"]].std().reset_index()
)
spatial_dispersion_df["spatial_dispersion"] = (
    spatial_dispersion_df["地點LAT"] + spatial_dispersion_df["地點LNG"]
)
spatial_dispersion_df.rename(
    columns={"地點LAT": "lat_std", "地點LNG": "lng_std"}, inplace=True
)
# spatial_dispersion_df.head()

# Define the original CRS (WGS84) and the target CRS (a projected CRS, e.g., TWD97 / TM2 zone north - epsg:3826)
# Note: TWD97 is appropriate for Taiwan. Use a different CRS if the data is elsewhere.
# Find appropriate CRS here: https://epsg.io/
transformer = Transformer.from_crs(CRS("epsg:4326"), CRS("epsg:3826"), always_xy=True)


def calculate_spatial_dispersion_projected(df):
    # Convert lat/lng to Point objects and project to a suitable CRS
    geometry = [Point(xy) for xy in zip(df["地點LNG"], df["地點LAT"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="epsg:4326")

    # Apply the transformation
    gdf["geometry_projected"] = gdf["geometry"].apply(
        lambda point: Point(transformer.transform(point.x, point.y))
    )

    # Group by region and calculate the centroid of the projected points
    region_centroids = gdf.groupby(["場所縣市", "場所區域"])[
        "geometry_projected"
    ].apply(lambda points: points.unary_union.centroid)

    # Calculate the distance of each point to its region's centroid and then the standard deviation of these distances
    spatial_dispersion = {}
    for (county, region), centroid in region_centroids.items():
        region_aeds_projected = gdf[
            (gdf["場所縣市"] == county) & (gdf["場所區域"] == region)
        ]["geometry_projected"]
        distances = region_aeds_projected.apply(lambda point: point.distance(centroid))
        spatial_dispersion[(county, region)] = distances.std()

    # Convert the dictionary to a DataFrame
    spatial_dispersion_df_projected = pd.DataFrame.from_dict(
        spatial_dispersion, orient="index", columns=["spatial_dispersion_projected"]
    ).reset_index()
    spatial_dispersion_df_projected[["場所縣市", "場所區域"]] = pd.DataFrame(
        spatial_dispersion_df_projected["index"].tolist(),
        index=spatial_dispersion_df_projected.index,
    )
    spatial_dispersion_df_projected.drop(columns=["index"], inplace=True)

    return spatial_dispersion_df_projected


# Calculate spatial dispersion using projected coordinates
spatial_dispersion_projected_df = calculate_spatial_dispersion_projected(aed)
# spatial_dispersion_projected_df.head()

# Merge the spatial dispersion data with the combined count and per capita data
final_merged_df = pd.merge(
    merged_df,
    spatial_dispersion_projected_df,
    on=["場所縣市", "場所區域"],
    how="left",
)

final_merged_df.fillna(0, inplace=True)  # Fill missing dispersion values with 0
# final_merged_df.head()

# Display the relevant columns for the final result
final_result = final_merged_df[
    [
        "場所縣市",
        "場所區域",
        "aed_count",
        "人口數",
        "people_per_aed",
        "spatial_dispersion_projected",
    ]
]
final_result["people_per_aed"] = final_result["people_per_aed"].astype(int)
final_result["spatial_dispersion_projected"] = final_result[
    "spatial_dispersion_projected"
].astype(int)
# final_result.head()

# 儲存雙北結果
final_result.to_csv(
    data_ws + "component_ready/" + "people_per_aed_spatial_dispersion.csv", index=False
)

# 儲存臺北市結果
final_result_tp = final_result[final_result["場所縣市"] == "臺北市"]
final_result_tp.to_csv(
    data_ws + "component_ready/" + "people_per_aed_spatial_dispersion_tp.csv",
    index=False,
)
