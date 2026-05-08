from markupsafe import Markup
from flask import Flask, jsonify, redirect, render_template, request

from .config import get_config
from .helpers import build_client_location
from .store import StateStore
from .services.charts import build_trend_svg
from .services.dashboard import DashboardError, DashboardService


def create_app(config=None):
    config = config or get_config()
    app = Flask(
        __name__,
        template_folder=str(config.template_dir),
        static_folder=str(config.static_dir),
    )
    app.config["JSON_AS_ASCII"] = False
    app.json.ensure_ascii = False
    app.config["HOST"] = config.host
    app.config["PORT"] = config.port

    store = StateStore(config.state_file)
    dashboard_service = DashboardService(config)

    def load_dashboard_for_response():
        current_state = store.read()
        location = current_state.get("location")
        if not location:
            raise DashboardError("服务器中还没有定位记录，请先完成定位。")

        dashboard = dashboard_service.fetch(location)
        store.save_dashboard(dashboard)
        return dashboard

    @app.get("/")
    def home():
        current_state = store.read()
        dashboard = None
        trend_svg = ""
        error_message = ""
        if current_state.get("location"):
            try:
                dashboard = load_dashboard_for_response()
                trend_svg = Markup(build_trend_svg(dashboard.get("hourlyTrend", [])))
            except DashboardError as error:
                error_message = str(error)

        return render_template(
            "index.html",
            baidu_map_ak=config.baidu_map_ak,
            location=current_state.get("location"),
            dashboard=dashboard,
            trend_svg=trend_svg,
            error_message=error_message,
        )

    @app.get("/details.html")
    def details():
        return redirect("/")

    @app.post("/api/location")
    def save_location():
        payload = request.get_json(silent=True) or {}
        try:
            location = build_client_location(payload)
        except ValueError as error:
            return jsonify({"ok": False, "message": str(error)}), 400

        store.save_location(location)
        return jsonify({"ok": True, "location": location})

    @app.get("/api/dashboard")
    def dashboard_api():
        try:
            dashboard = load_dashboard_for_response()
            return jsonify(dashboard)
        except DashboardError as error:
            status_code = 404 if "还没有定位记录" in str(error) else 502
            return jsonify({"ok": False, "message": str(error)}), status_code

    return app
