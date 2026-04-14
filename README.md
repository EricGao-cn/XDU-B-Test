# 雾霾探测系统设计

这个仓库现在使用 `uv` 管理 Python 版本、依赖、锁文件和虚拟环境，是一个纯 Python 的最小 Web demo，用来展示题目要求的核心链路：

- 首页通过百度地图 API 获取定位城市
- 定位结果保存到 Flask 服务端并持久化到本地 JSON
- 详情页展示天气、空气质量和未来 24 小时趋势
- 默认支持 `mock` 模式演示，也可切到 `live` 模式请求和风天气
- 继续保留截图脚本和 `docx` 实验报告生成

## 技术栈

- 后端：Flask
- 前端：Jinja 模板 + 原生 JavaScript
- 数据持久化：`data/app-state.json`
- 实时天气：和风天气 API（仅 `APP_DATA_MODE=live` 时启用）
- 截图：Python Playwright
- 报告生成：Python + `python-docx`

## 环境与启动

1. 安装 `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 进入项目后同步环境

```bash
uv sync
```

这一步会自动：

- 按 `.python-version` 安装并使用 Python 3.12
- 创建项目虚拟环境 `.venv`
- 根据 `pyproject.toml` 和 `uv.lock` 安装依赖

3. 复制环境变量文件

```bash
cp .env.example .env
```

默认只需要：

- `PORT`
- `APP_DATA_MODE=mock`

如需在浏览器里使用真实百度定位，还需要：

- `BAIDU_MAP_AK`

如需切到真实天气接口，还需要：

- `QWEATHER_API_HOST`
- `QWEATHER_API_KEY`

4. 启动服务

```bash
uv run python app.py
```

打开 [http://127.0.0.1:3000](http://127.0.0.1:3000)。

## 模式说明

### `mock` 模式

- 默认模式
- 不依赖和风天气密钥
- 使用 `data/mock-dashboard.json` 作为模板数据
- 仍会把最新定位结果写入 `data/app-state.json`

### `live` 模式

- 需要真实 `QWEATHER_API_HOST` 和 `QWEATHER_API_KEY`
- 服务端会根据当前定位调用和风天气接口

## 项目结构

```text
.
├── app.py                       # Flask 启动入口
├── smog_demo/                   # Python 服务端逻辑
├── templates/                   # 页面模板
├── static/                      # 静态资源
├── data/app-state.json          # 服务端定位与天气快照
├── data/mock-dashboard.json     # mock 模式模板数据
├── scripts/capture_screenshots.py
└── scripts/generate_report.py
```

## 接口

- `POST /api/location`
- `GET /api/dashboard`

## 运行测试

```bash
uv run pytest
```

## 截图与报告

先启动本地服务，再执行：

```bash
uv run python scripts/capture_screenshots.py
uv run python scripts/generate_report.py
```

如果本机没有可直接调用的 Chrome，可先安装 Playwright 浏览器：

```bash
uv run playwright install chromium
```

输出文件：

- `output/screenshots/home.png`
- `output/screenshots/details.png`
- `output/doc/雾霾探测系统设计实验报告.docx`
