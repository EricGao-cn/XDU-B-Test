import json
from pathlib import Path


DEFAULT_STATE = {"location": None, "dashboard": None}


class StateStore:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self._ensure_file()

    def _ensure_file(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text(
                json.dumps(DEFAULT_STATE, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def read(self):
        self._ensure_file()
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def write(self, next_state):
        self._ensure_file()
        self.file_path.write_text(
            json.dumps(next_state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return next_state

    def save_location(self, location):
        current = self.read()
        current["location"] = location
        return self.write(current)

    def save_dashboard(self, dashboard):
        current = self.read()
        current["dashboard"] = dashboard
        return self.write(current)
