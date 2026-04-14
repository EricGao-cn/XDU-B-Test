import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
APP_ORIGIN = os.environ.get("APP_ORIGIN", "http://127.0.0.1:3000")
DEFAULT_CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def get_executable_path():
    configured = os.environ.get("CHROME_PATH", "").strip()
    if configured:
        return configured
    if Path(DEFAULT_CHROME_PATH).exists():
        return DEFAULT_CHROME_PATH
    return None


def main():
    (ROOT / "output" / "screenshots").mkdir(parents=True, exist_ok=True)
    errors = []

    with sync_playwright() as playwright:
        launch_args = {"headless": True}
        executable_path = get_executable_path()
        if executable_path:
            launch_args["executable_path"] = executable_path

        browser = playwright.chromium.launch(**launch_args)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
        )

        home = context.new_page()
        home.on(
            "console",
            lambda msg: errors.append(f"home:{msg.type}:{msg.text}")
            if msg.type in {"error", "warning"}
            else None,
        )
        home.on("pageerror", lambda error: errors.append(f"home:pageerror:{error}"))
        home.add_init_script(
            """
            window.BMAP_STATUS_SUCCESS = 0;
            window.BMap = {
              Geolocation: function Geolocation() {
                this.enableSDKLocation = function () {};
                this.getCurrentPosition = function getCurrentPosition(callback) {
                  setTimeout(function () {
                    callback.call(
                      { getStatus: function () { return 0; } },
                      {
                        address: { city: "北京市", province: "北京市", district: "海淀区" },
                        point: { lng: 116.4039, lat: 39.9151 }
                      }
                    );
                  }, 120);
                };
              },
              LocalCity: function LocalCity() {
                this.get = function get(callback) {
                  callback({ name: "北京市", center: { lng: 116.4039, lat: 39.9151 } });
                };
              }
            };
            """
        )
        home.goto(f"{APP_ORIGIN}/", wait_until="domcontentloaded")
        home.click("#locate-button")
        home.wait_for_function(
            "document.querySelector('#city-name') && document.querySelector('#city-name').textContent.includes('北京')"
        )
        home.screenshot(path=str(ROOT / "output" / "screenshots" / "home.png"))

        details = context.new_page()
        details.on(
            "console",
            lambda msg: errors.append(f"details:{msg.type}:{msg.text}")
            if msg.type in {"error", "warning"}
            else None,
        )
        details.on("pageerror", lambda error: errors.append(f"details:pageerror:{error}"))
        details.goto(f"{APP_ORIGIN}/details.html", wait_until="domcontentloaded")
        details.wait_for_function(
            """
            document.querySelector('#aqi-value') &&
            document.querySelector('#aqi-value').textContent.trim() !== '-'
            """
        )
        details.screenshot(path=str(ROOT / "output" / "screenshots" / "details.png"))

        browser.close()

    print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
