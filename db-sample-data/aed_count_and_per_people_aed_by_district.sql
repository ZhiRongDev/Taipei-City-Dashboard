/* 雙北行政區內AED自動體外心臟去顫器數量並且平均多少人數共用一台AED自動體外心臟去顫器 */
SELECT x_axis, y_axis, data
FROM (
    SELECT
        場所區域 AS x_axis,
        'aed_count' AS y_axis,
        aed_count AS data
    FROM people_per_aed_spatial_dispersion
    WHERE 場所縣市 = '臺北市' OR 場所縣市 = '新北市'
    GROUP BY 場所區域, aed_count, people_per_aed

    UNION ALL

    SELECT
        場所區域 AS x_axis,
        'people_per_aed' AS y_axis,
        people_per_aed AS data
    FROM people_per_aed_spatial_dispersion
    WHERE 場所縣市 = '臺北市' OR 場所縣市 = '新北市'
    GROUP BY 場所區域, aed_count, people_per_aed
) t
ORDER BY
    ARRAY_POSITION(
        ARRAY[
            '北投區', '士林區', '內湖區', '南港區', '松山區', '信義區', '中山區', '大同區', '中正區', '萬華區', '大安區', '文山區',
            '新莊區', '淡水區', '汐止區', '板橋區', '三重區', '樹林區', '土城區', '蘆洲區', '中和區', '永和區', '新店區', '鶯歌區',
            '三峽區', '瑞芳區', '五股區', '泰山區', '林口區', '深坑區', '石碇區', '坪林區', '三芝區', '石門區', '八里區', '平溪區',
            '雙溪區', '貢寮區', '金山區', '萬里區', '烏來區'
        ], x_axis
    ),
    CASE y_axis
        WHEN 'people_per_aed' THEN 1
        WHEN 'aed_count' THEN 2
        ELSE 3
    END

/* 臺北市行政區內AED自動體外心臟去顫器數量並且平均多少人數共用一台AED自動體外心臟去顫器 */
SELECT x_axis, y_axis, data
FROM (
    SELECT
        場所區域 AS x_axis,
        'aed_count' AS y_axis,
        aed_count AS data
    FROM people_per_aed_spatial_dispersion_tp
    WHERE 場所縣市 = '臺北市'
    GROUP BY 場所區域, aed_count, people_per_aed

    UNION ALL

    SELECT
        場所區域 AS x_axis,
        'people_per_aed' AS y_axis,
        people_per_aed AS data
    FROM people_per_aed_spatial_dispersion_tp
    WHERE 場所縣市 = '臺北市'
    GROUP BY 場所區域, aed_count, people_per_aed
) t
ORDER BY
    ARRAY_POSITION(
        ARRAY[
            '北投區', '士林區', '內湖區', '南港區', '松山區', '信義區', '中山區', '大同區', '中正區', '萬華區', '大安區', '文山區',
            '新莊區', '淡水區', '汐止區', '板橋區', '三重區', '樹林區', '土城區', '蘆洲區', '中和區', '永和區', '新店區', '鶯歌區',
            '三峽區', '瑞芳區', '五股區', '泰山區', '林口區', '深坑區', '石碇區', '坪林區', '三芝區', '石門區', '八里區', '平溪區',
            '雙溪區', '貢寮區', '金山區', '萬里區', '烏來區'
        ], x_axis
    ),
    CASE y_axis
        WHEN 'people_per_aed' THEN 1
        WHEN 'aed_count' THEN 2
        ELSE 3
    END
