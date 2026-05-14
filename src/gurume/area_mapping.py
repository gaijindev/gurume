"""Map area names to Tabelog URL slugs."""

from __future__ import annotations

# Prefecture mapping.
PREFECTURE_MAPPING = {
    # Hokkaido and Tohoku.
    "北海道": "hokkaido",
    "青森県": "aomori",
    "岩手県": "iwate",
    "宮城県": "miyagi",
    "秋田県": "akita",
    "山形県": "yamagata",
    "福島県": "fukushima",
    # Kanto.
    "茨城県": "ibaraki",
    "栃木県": "tochigi",
    "群馬県": "gunma",
    "埼玉県": "saitama",
    "千葉県": "chiba",
    "東京都": "tokyo",
    "神奈川県": "kanagawa",
    # Chubu.
    "新潟県": "niigata",
    "富山県": "toyama",
    "石川県": "ishikawa",
    "福井県": "fukui",
    "山梨県": "yamanashi",
    "長野県": "nagano",
    "岐阜県": "gifu",
    "静岡県": "shizuoka",
    "愛知県": "aichi",
    # Kinki.
    "三重県": "mie",
    "滋賀県": "shiga",
    "京都府": "kyoto",
    "大阪府": "osaka",
    "兵庫県": "hyogo",
    "奈良県": "nara",
    "和歌山県": "wakayama",
    # Chugoku.
    "鳥取県": "tottori",
    "島根県": "shimane",
    "岡山県": "okayama",
    "広島県": "hiroshima",
    "山口県": "yamaguchi",
    # Shikoku.
    "徳島県": "tokushima",
    "香川県": "kagawa",
    "愛媛県": "ehime",
    "高知県": "kochi",
    # Kyushu and Okinawa.
    "福岡県": "fukuoka",
    "佐賀県": "saga",
    "長崎県": "nagasaki",
    "熊本県": "kumamoto",
    "大分県": "oita",
    "宮崎県": "miyazaki",
    "鹿児島県": "kagoshima",
    "沖縄県": "okinawa",
}

# Major city mapping without prefecture suffixes.
CITY_MAPPING = {
    "東京": "tokyo",
    "大阪": "osaka",
    "京都": "kyoto",
    "北海道": "hokkaido",
    "福岡": "fukuoka",
}

# City-level Tabelog paths. Prefecture-only slugs return overly broad cross-city results for these cities.
CITY_AREA_PATH_MAPPING = {
    "札幌": "hokkaido/A0101",
    "名古屋": "aichi/A2301",
    "神戸": "hyogo/A2801",
}

# Sub-area Tabelog paths. These narrow searches to a specific neighborhood within a city.
# Codes are taken from Tabelog's URL structure (e.g. tokyo/A1302/A130202 for Nihonbashi).
SUB_AREA_PATH_MAPPING = {
    # Tokyo: A1301 — Ginza/Shimbashi/Yurakucho area.
    "銀座": "tokyo/A1301/A130101",
    "新橋": "tokyo/A1301/A130103",
    "有楽町": "tokyo/A1301/A130102",
    # Tokyo: A1302 — Tokyo Station / Nihonbashi area.
    "丸の内": "tokyo/A1302/A130201",
    "大手町": "tokyo/A1302/A130201",
    "日本橋": "tokyo/A1302/A130202",
    "京橋": "tokyo/A1302/A130202",
    "茅場町": "tokyo/A1302/A130203",
    "八丁堀": "tokyo/A1302/A130203",
    "人形町": "tokyo/A1302/A130204",
    "小伝馬町": "tokyo/A1302/A130204",
    # Tokyo: A1303 — Roppongi/Azabu/Hiroo.
    "六本木": "tokyo/A1307/A130701",
    "麻布": "tokyo/A1307/A130702",
    "広尾": "tokyo/A1307/A130703",
    # Tokyo: A1304 — Shinjuku/Yotsuya.
    "新宿": "tokyo/A1304/A130401",
    "四谷": "tokyo/A1309/A130901",
    # Tokyo: A1305 — Ikebukuro.
    "池袋": "tokyo/A1305/A130501",
    # Tokyo: A1306 — Harajuku/Aoyama/Shibuya.
    "渋谷": "tokyo/A1303/A130301",
    "原宿": "tokyo/A1306/A130603",
    "表参道": "tokyo/A1306/A130603",
    "青山": "tokyo/A1306/A130602",
    # Tokyo: A1311 — Ueno/Asakusa.
    "上野": "tokyo/A1311/A131101",
    "浅草": "tokyo/A1311/A131102",
    # Tokyo: A1314 — Shinagawa.
    "品川": "tokyo/A1314/A131401",
    # Osaka.
    "梅田": "osaka/A2701/A270101",
    "難波": "osaka/A2701/A270202",
    "心斎橋": "osaka/A2701/A270201",
    # Kyoto.
    "祇園": "kyoto/A2601/A260301",
    "河原町": "kyoto/A2601/A260301",
}

# Reverse lookup from prefecture names without suffixes to slugs.
_PREFIX_TO_SLUG = {}
for full_name, slug in PREFECTURE_MAPPING.items():
    # Remove prefecture suffixes.
    for suffix in ["都", "府", "県"]:
        if full_name.endswith(suffix):
            prefix = full_name[: -len(suffix)]
            _PREFIX_TO_SLUG[prefix] = slug
            break


def _lookup_area_path(area_name: str) -> str | None:
    # Sub-area lookup runs first so neighborhood names like "日本橋" resolve to the narrow
    # Tabelog path rather than the broader city slug.
    if area_name in SUB_AREA_PATH_MAPPING:
        return SUB_AREA_PATH_MAPPING[area_name]
    if area_name in PREFECTURE_MAPPING:
        return PREFECTURE_MAPPING[area_name]
    if area_name in CITY_MAPPING:
        return CITY_MAPPING[area_name]
    if area_name in CITY_AREA_PATH_MAPPING:
        return CITY_AREA_PATH_MAPPING[area_name]
    if area_name in _PREFIX_TO_SLUG:
        return _PREFIX_TO_SLUG[area_name]
    return None


def get_area_slug(area_name: str) -> str | None:
    """
    Convert an area name to a Tabelog URL slug or path.

    Args:
        area_name: Area name, for example "東京都", "東京", "大阪府", "三重", or "札幌".

    Returns:
        URL slug/path, for example "tokyo", "mie", or "hokkaido/A0101"; otherwise None.
    """
    # Check full names, city names, city-level paths, and prefecture-name prefixes first.
    area_path = _lookup_area_path(area_name)
    if area_path:
        return area_path

    # Remove prefecture/city suffixes, then try again.
    for suffix in ["都", "府", "県", "市"]:
        if area_name.endswith(suffix):
            return _lookup_area_path(area_name[: -len(suffix)])

    return None
