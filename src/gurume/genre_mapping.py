"""Map cuisine names to genre codes and search path segments."""

from __future__ import annotations

# Tabelog cuisine genre codes (RC = Restaurant Category).
# Format: cuisine name -> URL code.
GENRE_CODE_MAPPING = {
    # Japanese cuisine.
    "すき焼き": "RC0107",
    "しゃぶしゃぶ": "RC0106",
    "寿司": "RC0201",
    "天ぷら": "RC0301",
    "とんかつ": "RC0302",
    "焼き鳥": "RC0401",
    "ラーメン": "RC0501",
    "うどん": "RC0601",
    "そば": "RC0602",
    "うなぎ": "RC0701",
    "日本料理": "RC0801",
    "海鮮": "RC0901",
    # Western-style cuisine.
    "フレンチ": "RC1001",
    "イタリアン": "RC1101",
    "ステーキ": "RC1201",
    "ハンバーグ": "RC1202",
    "ハンバーガー": "RC1203",
    "洋食": "RC1301",
    # Chinese cuisine.
    "中華料理": "RC1401",
    "餃子": "RC1402",
    # Yakiniku.
    "焼肉": "RC1501",
    "ホルモン": "RC1502",
    # Hot pot.
    "鍋": "RC1601",
    "もつ鍋": "RC1602",
    # Izakaya.
    "居酒屋": "RC1701",
    # Curry.
    "カレー": "RC1801",
    # Other.
    "カフェ": "RC1901",
    "パン": "RC2001",
    "スイーツ": "RC2101",
}

# Extended cuisine codes harvested from Tabelog's current category index
# (https://tabelog.com/rstLst/RC/ and its child pages, May 2026).
# These cover ~209 cuisines — top-level (RCxx), mid-level (RCxxxx), and leaf
# (RCxxxxxx) categories. Names in GENRE_CODE_MAPPING above take precedence so
# the legacy short codes used by older code paths remain authoritative.
EXTENDED_GENRE_CODE_MAPPING = {
    # Top-level categories (RCxx).
    "和食": "RC01",
    "洋食・西洋料理": "RC02",
    "中華": "RC03",
    "アジア・エスニック": "RC04",
    "カレー・スパイス料理": "RC12",
    "焼肉・ホルモン": "RC13",
    "居酒屋・ダイニングバー": "RC21",
    "その他レストラン": "RC98",
    # 和食 — sushi/japanese variants.
    "日本料理・割烹・懐石": "RC010110",
    "回転寿司": "RC010202",
    "立ち食い寿司": "RC010203",
    "いなり寿司": "RC010204",
    "鯖寿司・棒寿司": "RC010205",
    "立ち食いそば": "RC010408",
    "どじょう": "RC010502",
    "あなご": "RC010503",
    # 焼き鳥・串焼・鳥料理 (RC0106) collides with legacy しゃぶしゃぶ; use specific leaves below.
    "串焼き": "RC010602",
    "鳥料理": "RC010603",
    "もつ焼き・焼きとん": "RC010604",
    "手羽先": "RC010606",
    "おでん": "RC0108",
    "お好み焼き・たこ焼き": "RC0109",
    "たこ焼き": "RC010911",
    "明石焼き": "RC010912",
    "丼": "RC0111",
    "牛丼": "RC011101",
    "親子丼": "RC011102",
    "天丼": "RC011103",
    "かつ丼": "RC011104",
    "海鮮丼": "RC011105",
    "豚丼": "RC011106",
    "海鮮・魚介": "RC011211",
    "ふぐ": "RC011212",
    "蟹": "RC011213",
    "すっぽん": "RC011214",
    "あんこう": "RC011215",
    "牡蠣": "RC011216",
    "豚しゃぶ": "RC012102",
    "カレーうどん": "RC012302",
    "麺類": "RC0124",
    "焼きそば": "RC012402",
    "沖縄そば": "RC012403",
    "ほうとう": "RC012404",
    "ちゃんぽん": "RC012405",
    "とんかつ・揚げ物": "RC0125",
    "牛カツ": "RC012502",
    "唐揚げ": "RC012504",
    "揚げ物・フライ": "RC012505",
    "炉端焼き": "RC019903",
    "牛タン": "RC019907",
    "麦とろ": "RC019908",
    "釜飯": "RC019909",
    "豆腐料理・湯葉料理": "RC019910",
    "鯨": "RC019911",
    "お茶漬け": "RC019913",
    "郷土料理": "RC019914",
    "きりたんぽ": "RC019916",
    # Western.
    # ステーキ・鉄板焼 (RC0201) collides with legacy 寿司; access via 鉄板焼き leaf below.
    "鉄板焼き": "RC020103",
    "オムライス": "RC020912",
    "スープ": "RC020914",
    "コロッケ": "RC020915",
    "ビストロ": "RC021102",
    "スペイン料理": "RC021301",
    "ヨーロッパ料理": "RC0219",
    "ドイツ料理": "RC021903",
    "ロシア料理": "RC021904",
    "ポルトガル料理": "RC021910",
    "ギリシャ料理": "RC021911",
    "アメリカ料理": "RC0220",
    "カリフォルニア料理": "RC022002",
    "ハワイ料理": "RC022003",
    "ホットドッグ": "RC022005",
    # Chinese.
    "中華粥": "RC0303",
    "四川料理": "RC0305",
    "台湾料理": "RC0306",
    "飲茶・点心": "RC0307",
    "肉まん": "RC0309",
    "小籠包": "RC0310",
    # Asian / Ethnic.
    "韓国料理": "RC040101",
    "冷麺": "RC040102",
    "東南アジア料理": "RC0402",
    "ベトナム料理": "RC040202",
    "インドネシア料理": "RC040203",
    "シンガポール料理": "RC040204",
    "バインミー": "RC040205",
    "南アジア料理": "RC0403",
    "インド料理": "RC040301",
    "ネパール料理": "RC040302",
    "パキスタン料理": "RC040303",
    "スリランカ料理": "RC040304",
    "中東料理": "RC0404",
    "トルコ料理": "RC040401",
    "ケバブ": "RC040402",
    "モロッコ料理": "RC040403",
    "ファラフェル": "RC040404",
    "中南米料理": "RC0411",
    "メキシコ料理": "RC041101",
    "ブラジル料理": "RC041102",
    "シュラスコ": "RC041103",
    "タコス": "RC041104",
    "ペルー料理": "RC041105",
    "アフリカ料理": "RC0412",
    # Curry.
    # RC1203 mid-level collides with legacy ハンバーガー; use leaf code.
    "インドカレー": "RC120301",
    "スープカレー": "RC120501",
    # Yakiniku.
    "ジンギスカン": "RC1302",
    # Nabe / hot pot.
    # RC1401/RC1402 mid-levels collide with legacy 中華料理/餃子; use leaf codes.
    "ちゃんこ鍋": "RC140101",
    "うどんすき": "RC140201",
    "水炊き": "RC1404",
    "火鍋": "RC1406",
    # Izakaya / bars.
    "ダイニングバー": "RC2102",
    "バル": "RC2103",
    "肉バル": "RC210302",
    "ビアガーデン・ビアホール": "RC2104",
    "ビアガーデン": "RC210401",
    "ビアホール・ビアレストラン": "RC210402",
    "立ち飲み": "RC2105",
    # Other.
    "レストラン・食堂": "RC9801",
    "レストラン": "RC980101",
    "ファミレス": "RC980102",
    "学生食堂": "RC980104",
    "社員食堂": "RC980105",
    "創作料理・イノベーティブ": "RC9802",
    "創作料理": "RC980201",
    "イノベーティブ": "RC980202",
    "オーガニック・薬膳": "RC9803",
    "オーガニック": "RC980301",
    "薬膳": "RC980302",
    "弁当・おにぎり・惣菜": "RC9804",
    "弁当": "RC980401",
    "おにぎり": "RC980402",
    "惣菜・デリ": "RC980403",
    "肉料理": "RC9805",
    "牛料理": "RC980502",
    "豚料理": "RC980503",
    "馬肉料理": "RC980504",
    "ジビエ料理": "RC980505",
    "シーフード": "RC9806",
    "オイスターバー": "RC980602",
    "サラダ・野菜料理": "RC9807",
    "サラダ": "RC980701",
    "野菜料理": "RC980702",
    "チーズ料理": "RC9808",
    "にんにく料理": "RC9809",
    "ビュッフェ・バイキング": "RC981001",
    "バーベキュー": "RC9811",
    "屋形船・クルージング": "RC9812",
}

# Convenience aliases — Tabelog tags some cuisines under multiple common names.
GENRE_ALIASES = {
    "ビュッフェ": "ビュッフェ・バイキング",
    "バイキング": "ビュッフェ・バイキング",
    "焼鳥": "焼き鳥",
    "焼そば": "焼きそば",
    "焼肉ホルモン": "焼肉・ホルモン",
    "鉄板焼": "鉄板焼き",
}

# Current Tabelog search pages encode cuisine filters in URL path segments instead of the legacy LstG query.
# Most cuisines use SEO slugs, but some live search pages still use category-code path segments.
CUISINE_SLUG_MAPPING = {
    "すき焼き": "RC0107",
    "しゃぶしゃぶ": "syabusyabu",
    "寿司": "sushi",
    "天ぷら": "tempura",
    "とんかつ": "tonkatsu",
    "焼き鳥": "yakitori",
    "ラーメン": "MC0101",
    "うどん": "udon",
    "そば": "soba",
    "うなぎ": "unagi",
    "日本料理": "japanese",
    "海鮮": "seafood",
    "フレンチ": "french",
    "イタリアン": "italian",
    "ステーキ": "steak",
    "ハンバーグ": "hamburgersteak",
    "ハンバーガー": "hamburger",
    "洋食": "yoshoku",
    "中華料理": "chinese",
    "餃子": "gyouza",
    "焼肉": "yakiniku",
    "ホルモン": "horumon",
    "鍋": "nabe",
    "もつ鍋": "motsu",
    "居酒屋": "izakaya",
    "カレー": "curry",
    "カフェ": "cafe",
    "パン": "pan",
    "スイーツ": "sweets",
}


def get_genre_code(genre_name: str) -> str | None:
    """
    Convert a cuisine name to a Tabelog URL code.

    Looks up names in the legacy ``GENRE_CODE_MAPPING`` first so historical short
    codes (e.g. ``寿司`` → ``RC0201``) remain authoritative, then falls back to
    the extended mapping (~150 additional cuisines harvested from Tabelog's
    current category index), and finally consults ``GENRE_ALIASES``.

    Args:
        genre_name: Cuisine name, for example "すき焼き", "寿司", or "ビュッフェ".

    Returns:
        URL code, for example "RC0107"; otherwise None.
    """
    if genre_name in GENRE_CODE_MAPPING:
        return GENRE_CODE_MAPPING[genre_name]
    if genre_name in EXTENDED_GENRE_CODE_MAPPING:
        return EXTENDED_GENRE_CODE_MAPPING[genre_name]
    if genre_name in GENRE_ALIASES:
        return get_genre_code(GENRE_ALIASES[genre_name])
    return None


def get_genre_name_by_code(genre_code: str) -> str | None:
    """
    Look up a cuisine name by code. Legacy mapping wins over extended mapping.

    Args:
        genre_code: URL code, for example "RC0107".

    Returns:
        Cuisine name, or None.
    """
    for name, code in GENRE_CODE_MAPPING.items():
        if code == genre_code:
            return name
    for name, code in EXTENDED_GENRE_CODE_MAPPING.items():
        if code == genre_code:
            return name
    return None


def get_cuisine_slug(genre_name: str) -> str | None:
    """Get the Tabelog path segment for area + cuisine searches."""
    return CUISINE_SLUG_MAPPING.get(genre_name)


def get_cuisine_slug_by_code(genre_code: str) -> str | None:
    """Look up the current cuisine path segment from a legacy genre code."""
    genre_name = get_genre_name_by_code(genre_code)
    if not genre_name:
        return None
    return get_cuisine_slug(genre_name)


def get_all_genres() -> list[str]:
    """
    Get all supported cuisine names.

    Returns:
        List of cuisine names.
    """
    # Remove duplicates.
    return sorted(set(GENRE_CODE_MAPPING) | set(EXTENDED_GENRE_CODE_MAPPING))
