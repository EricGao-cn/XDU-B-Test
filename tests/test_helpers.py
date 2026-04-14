from smog_demo.helpers import build_client_location, format_coordinate_pair, normalize_city_name


def test_normalize_city_name_strips_trailing_city_suffix():
    assert normalize_city_name("西安市") == "西安"
    assert normalize_city_name("上海") == "上海"


def test_format_coordinate_pair_keeps_two_decimals():
    assert format_coordinate_pair(116.4039, 39.9151) == "116.40,39.92"


def test_build_client_location_normalizes_payload():
    result = build_client_location(
        {
            "city": "北京市",
            "province": "北京市",
            "district": "海淀区",
            "longitude": "116.4039",
            "latitude": "39.9151",
            "source": "gps",
            "locatedAt": "2026-04-07T21:00:00.000Z",
        }
    )

    assert result["city"] == "北京"
    assert result["longitude"] == 116.4039
    assert result["latitude"] == 39.9151
    assert result["source"] == "gps"


def test_build_client_location_requires_coordinates():
    try:
        build_client_location({"city": "北京市"})
    except ValueError as error:
        assert "定位坐标不能为空" in str(error)
    else:
        raise AssertionError("expected ValueError")
