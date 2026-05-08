import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_file(dotenv_path):
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _normalize_api_host(host):
    trimmed = host.strip().rstrip("/")
    if trimmed.startswith("http://") or trimmed.startswith("https://"):
        return trimmed
    return f"https://{trimmed}"


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    template_dir: Path
    static_dir: Path
    state_file: Path
    mock_dashboard_file: Path
    baidu_map_ak: str
    data_mode: str
    qweather_api_host: str
    qweather_api_key: str
    host: str
    port: int


def get_config():
    root_dir = Path(__file__).resolve().parents[1]
    _load_dotenv_file(root_dir / ".env")

    data_mode = os.environ.get("APP_DATA_MODE", "mock").strip().lower() or "mock"
    if data_mode not in {"mock", "live"}:
        data_mode = "mock"

    qweather_host = os.environ.get("QWEATHER_API_HOST", "").strip()
    qweather_key = os.environ.get("QWEATHER_API_KEY", "").strip()

    return AppConfig(
        root_dir=root_dir,
        template_dir=root_dir / "templates",
        static_dir=root_dir / "static",
        state_file=root_dir / "data" / "app-state.json",
        mock_dashboard_file=root_dir / "data" / "mock-dashboard.json",
        baidu_map_ak=os.environ.get("BAIDU_MAP_AK", "").strip(),
        data_mode=data_mode,
        qweather_api_host=_normalize_api_host(qweather_host) if qweather_host else "",
        qweather_api_key=qweather_key,
        host=os.environ.get("HOST", "127.0.0.1").strip() or "127.0.0.1",
        port=int(os.environ.get("PORT", "3000")),
    )
