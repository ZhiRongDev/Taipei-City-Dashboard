/* 臺北市各區的避難所數量 */
SELECT
	鄉鎮 AS x_axis,
	'flood' AS y_axis,
	flood_shelter_count AS data
FROM
	public.disaster_proportions_tp
UNION ALL
SELECT
	鄉鎮 AS x_axis,
	'earthquake' AS y_axis,
	earthquake_shelter_count AS data
FROM
	public.disaster_proportions_tp
UNION ALL
SELECT
	鄉鎮 AS x_axis,
	'landslide' AS y_axis,
	landslide_shelter_count AS data
FROM
	public.disaster_proportions_tp
UNION ALL
SELECT
	鄉鎮 AS x_axis,
	'tsunami' AS y_axis,
	tsunami_shelter_count AS data
FROM
	public.disaster_proportions_tp;