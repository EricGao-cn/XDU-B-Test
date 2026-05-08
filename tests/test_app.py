from dataclasses import replace
from pathlib import Path

from smog_demo import create_app
from smog_demo.config import AppConfig


def build_config(tmp_path, data_mode="mock"):
    root_dir = Path(__file__).resolve().parents[1]
    return AppConfig(
        root_dir=root_dir,
        template_dir=root_dir / "templates",
        static_dir=root_dir / "static",
        state_file=tmp_path / "app-state.json",
        mock_dashboard_file=root_dir / "data" / "mock-dashboard.json",
        baidu_map_ak="fake-ak",
        data_mode=data_mode,
        qweather_api_host="https://example.com",
        qweather_api_key="fake-key",
        host="127.0.0.1",
        port=3000,
    )


def test_dashboard_requires_location(tmp_path):
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.get("/api/dashboard")
    data = response.get_json()
    assert response.status_code == 404
    assert data["ok"] is False


def test_save_location_and_fetch_mock_dashboard(tmp_path):
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    save_response = client.post(
        "/api/location",
        json={
            "city": "北京市",
            "province": "北京市",
            "district": "海淀区",
            "longitude": 116.4039,
            "latitude": 39.9151,
            "source": "gps",
        },
    )
    save_data = save_response.get_json()
    assert save_response.status_code == 200
    assert save_data["ok"] is True
    assert save_data["location"]["city"] == "北京"

    dashboard_response = client.get("/api/dashboard")
    dashboard_data = dashboard_response.get_json()
    assert dashboard_response.status_code == 200
    assert dashboard_data["location"]["city"] == "北京"
    assert dashboard_data["weatherNow"]["cityName"] == "北京"
    assert len(dashboard_data["hourlyTrend"]) == 24


def test_home_renders_dashboard_after_location_is_saved(tmp_path):
    app = create_app(build_config(tmp_path))
    client = app.test_client()
    client.post(
        "/api/location",
        json={
            "city": "北京市",
            "province": "北京市",
            "longitude": 116.4039,
            "latitude": 39.9151,
            "source": "gps",
        },
    )

    response = client.get("/")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'id="aqi-value"' in html
    assert 'id="trend-chart"' in html


def test_details_redirects_to_home(tmp_path):
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.get("/details.html")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_live_dashboard_errors_when_qweather_request_fails(tmp_path):
    config = replace(build_config(tmp_path, data_mode="live"), qweather_api_host="", qweather_api_key="")
    app = create_app(config)
    client = app.test_client()
    client.post(
        "/api/location",
        json={
            "city": "北京市",
            "province": "北京市",
            "district": "海淀区",
            "longitude": 116.4039,
            "latitude": 39.9151,
            "source": "gps",
        },
    )

    response = client.get("/api/dashboard")
    data = response.get_json()
    assert response.status_code == 502
    assert "QWEATHER" in data["message"]
