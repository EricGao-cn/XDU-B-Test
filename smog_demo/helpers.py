from datetime import datetime, timezone


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_city_name(value):
    return normalize_text(value).removesuffix("市")


def to_number(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def round_coordinate(value):
    number = to_number(value)
    if number is None:
        return None
    return round(number, 4)


def format_coordinate_pair(longitude, latitude):
    return f"{float(longitude):.2f},{float(latitude):.2f}"


def pick_air_index(indexes):
    if not isinstance(indexes, list) or not indexes:
        return None

    preferred = next(
        (item for item in indexes if item.get("code") and item.get("code") != "qaqi"),
        None,
    )
    return preferred or indexes[0]


def list_to_map(items):
    result = {}
    for item in items or []:
        code = item.get("code") if isinstance(item, dict) else None
        if code:
            result[code] = item
    return result


def current_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_client_location(payload):
    city = normalize_city_name(payload.get("city"))
    if not city:
        raise ValueError("定位城市不能为空")

    longitude = round_coordinate(payload.get("longitude"))
    latitude = round_coordinate(payload.get("latitude"))
    if longitude is None or latitude is None:
        raise ValueError("定位坐标不能为空")

    located_at = normalize_text(payload.get("locatedAt")) or current_timestamp()

    return {
        "city": city,
        "province": normalize_text(payload.get("province")),
        "district": normalize_text(payload.get("district")),
        "longitude": longitude,
        "latitude": latitude,
        "source": normalize_text(payload.get("source")) or "gps",
        "locatedAt": located_at,
        "savedAt": current_timestamp(),
    }
