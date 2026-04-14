from html import escape
from math import isfinite


def _to_float(value, fallback):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if isfinite(number) else fallback


def _format_hour(value):
    if not value:
        return "--:--"
    return str(value)[11:16]


def _build_points(values, left, top, width, height):
    if not values:
        return ""

    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        minimum -= 1
        maximum += 1

    step_x = width / max(len(values) - 1, 1)
    points = []
    for index, value in enumerate(values):
        x = left + index * step_x
        ratio = (value - minimum) / (maximum - minimum)
        y = top + height - (ratio * height)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def build_trend_svg(hourly_trend):
    if not hourly_trend:
        return ""

    temp_values = [_to_float(item.get("temp"), 0.0) for item in hourly_trend]
    humidity_values = [_to_float(item.get("humidity"), 0.0) for item in hourly_trend]
    labels = [_format_hour(item.get("time")) for item in hourly_trend]

    width = 720
    height = 240
    left = 44
    top = 24
    inner_width = width - 72
    inner_height = height - 72

    grid_lines = []
    for step in range(5):
        y = top + (inner_height / 4) * step
        grid_lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + inner_width}" y2="{y:.1f}" '
            'stroke="rgba(23,50,47,0.10)" stroke-width="1" />'
        )

    label_nodes = []
    if labels:
        x_step = inner_width / max(len(labels) - 1, 1)
        for index, label in enumerate(labels):
            if index not in {0, len(labels) - 1} and index % 4 != 0:
                continue
            x = left + x_step * index
            label_nodes.append(
                f'<text x="{x:.1f}" y="{top + inner_height + 24}" text-anchor="middle" '
                'font-size="10" fill="#5b7069">'
                f"{escape(label)}</text>"
            )

    temp_points = _build_points(temp_values, left, top, inner_width, inner_height)
    humidity_points = _build_points(humidity_values, left, top, inner_width, inner_height)

    return f"""
<svg id="trend-chart" viewBox="0 0 {width} {height}" class="trend-svg" aria-label="未来24小时温湿度趋势图" role="img">
  <rect x="0" y="0" width="{width}" height="{height}" rx="22" fill="#f6f9f8"></rect>
  {''.join(grid_lines)}
  <polyline points="{temp_points}" fill="none" stroke="#c77d1f" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></polyline>
  <polyline points="{humidity_points}" fill="none" stroke="#2d7564" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></polyline>
  {''.join(label_nodes)}
  <g transform="translate(44, 12)">
    <circle cx="0" cy="0" r="5" fill="#c77d1f"></circle>
    <text x="10" y="4" font-size="11" fill="#17322f">温度 (°C)</text>
    <circle cx="88" cy="0" r="5" fill="#2d7564"></circle>
    <text x="98" y="4" font-size="11" fill="#17322f">湿度 (%)</text>
  </g>
</svg>
""".strip()
