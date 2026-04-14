import copy
import json

import requests

from ..helpers import (
    current_timestamp,
    format_coordinate_pair,
    list_to_map,
    normalize_city_name,
    pick_air_index,
)


class DashboardError(RuntimeError):
    pass


class DashboardService:
    def __init__(self, config):
        self.config = config

    def fetch(self, location):
        if self.config.data_mode == "live":
            return self._fetch_live_dashboard(location)
        return self._fetch_mock_dashboard(location)

    def _fetch_mock_dashboard(self, location):
        try:
            template = json.loads(self.config.mock_dashboard_file.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise DashboardError("缺少 mock 数据文件，无法生成演示面板。") from error

        dashboard = copy.deepcopy(template)
        standardized_city = normalize_city_name(location.get("city")) or dashboard["weatherNow"]["cityName"]
        province_name = location.get("province") or dashboard["weatherNow"].get("provinceName", "")
        district_name = location.get("district") or dashboard["weatherNow"].get("districtName", "")

        dashboard["location"].update(location)
        dashboard["location"]["standardizedCity"] = standardized_city
        dashboard["location"]["standardizedProvince"] = province_name
        dashboard["location"]["locationId"] = dashboard["location"].get("locationId") or "mock-location"
        dashboard["weatherNow"]["cityName"] = standardized_city
        dashboard["weatherNow"]["provinceName"] = province_name
        dashboard["weatherNow"]["districtName"] = district_name
        dashboard["updatedAt"] = current_timestamp()
        return dashboard

    def _request_qweather(self, pathname, params):
        if not self.config.qweather_api_host or not self.config.qweather_api_key:
            raise DashboardError("live 模式缺少 QWEATHER_API_HOST 或 QWEATHER_API_KEY。")

        url = f"{self.config.qweather_api_host}/{pathname.lstrip('/')}"
        try:
            response = requests.get(
                url,
                params={key: value for key, value in (params or {}).items() if value not in ("", None)},
                headers={
                    "Accept": "application/json",
                    "X-QW-Api-Key": self.config.qweather_api_key,
                },
                timeout=15,
            )
        except requests.RequestException as error:
            raise DashboardError(f"和风天气请求失败: {error}") from error

        try:
            data = response.json()
        except ValueError as error:
            raise DashboardError(f"和风天气返回了无法解析的数据: {response.status_code}") from error

        if response.status_code >= 400:
            raise DashboardError(f"和风天气请求失败: HTTP {response.status_code}")

        if data.get("code") and data["code"] != "200":
            raise DashboardError(f"和风天气业务状态异常: {data['code']}")

        return data

    def _lookup_city(self, location):
        if location.get("longitude") is not None and location.get("latitude") is not None:
            query_location = format_coordinate_pair(location["longitude"], location["latitude"])
        else:
            query_location = normalize_city_name(location.get("city"))

        params = {"location": query_location, "range": "cn", "number": 1, "lang": "zh"}
        if location.get("province"):
            params["adm"] = location["province"]

        data = self._request_qweather("/geo/v2/city/lookup", params)
        locations = data.get("location") or []
        if not locations:
            raise DashboardError("未找到匹配的城市信息")
        return locations[0]

    def _fetch_live_dashboard(self, location):
        if location.get("longitude") is None or location.get("latitude") is None:
            raise DashboardError("缺少经纬度，无法查询空气质量")

        city_info = self._lookup_city(location)
        location_id = city_info["id"]

        weather_now = self._request_qweather(
            "/v7/weather/now",
            {"location": location_id, "unit": "m", "lang": "zh"},
        )
        hourly_weather = self._request_qweather(
            "/v7/weather/24h",
            {"location": location_id, "unit": "m", "lang": "zh"},
        )
        air_quality = self._request_qweather(
            f"/airquality/v1/current/{float(location['latitude']):.2f}/{float(location['longitude']):.2f}",
            {"lang": "zh"},
        )

        primary_index = pick_air_index(air_quality.get("indexes"))
        pollutants = list_to_map(air_quality.get("pollutants"))

        return {
            "location": {
                **location,
                "standardizedCity": city_info.get("name", ""),
                "standardizedProvince": city_info.get("adm1", ""),
                "locationId": city_info.get("id", ""),
            },
            "weatherNow": {
                "cityName": city_info.get("name", ""),
                "provinceName": city_info.get("adm1", ""),
                "districtName": city_info.get("adm2", ""),
                "observedAt": weather_now["now"]["obsTime"],
                "updatedAt": weather_now.get("updateTime", ""),
                "text": weather_now["now"]["text"],
                "icon": weather_now["now"]["icon"],
                "temp": weather_now["now"]["temp"],
                "feelsLike": weather_now["now"]["feelsLike"],
                "humidity": weather_now["now"]["humidity"],
                "windDir": weather_now["now"]["windDir"],
                "windSpeed": weather_now["now"]["windSpeed"],
                "windScale": weather_now["now"]["windScale"],
                "visibility": weather_now["now"]["vis"],
                "pressure": weather_now["now"]["pressure"],
                "fxLink": weather_now.get("fxLink", ""),
            },
            "airQuality": {
                "indexCode": primary_index["code"] if primary_index else "",
                "indexName": primary_index["name"] if primary_index else "",
                "aqi": primary_index["aqi"] if primary_index else "",
                "aqiDisplay": primary_index["aqiDisplay"] if primary_index else "",
                "level": primary_index["level"] if primary_index else "",
                "category": primary_index["category"] if primary_index else "",
                "primaryPollutant": primary_index.get("primaryPollutant") if primary_index else None,
                "health": primary_index.get("health") if primary_index else None,
                "pollutants": {
                    "pm2p5": pollutants.get("pm2p5"),
                    "pm10": pollutants.get("pm10"),
                    "no2": pollutants.get("no2"),
                    "so2": pollutants.get("so2"),
                    "co": pollutants.get("co"),
                    "o3": pollutants.get("o3"),
                },
                "stations": air_quality.get("stations") or [],
            },
            "hourlyTrend": [
                {
                    "time": item["fxTime"],
                    "temp": item["temp"],
                    "humidity": item["humidity"],
                    "text": item["text"],
                    "icon": item["icon"],
                }
                for item in (hourly_weather.get("hourly") or [])
            ],
            "updatedAt": current_timestamp(),
        }
