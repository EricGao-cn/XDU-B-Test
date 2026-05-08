# 雾霾探测系统设计

这个仓库现在使用 `uv` 管理 Python 版本、依赖、锁文件和虚拟环境，是一个纯 Python 的最小 Web demo，用来展示题目要求的核心链路：

- 首页通过百度地图 API 获取定位城市
- 定位结果保存到 Flask 服务端并持久化到本地 JSON
- 首页直接展示天气、空气质量和未来 24 小时趋势
- 默认支持 `mock` 模式演示，也可切到 `live` 模式请求和风天气
- 继续保留截图脚本和 `docx` 实验报告生成

## 技术栈

- 后端：Flask
- 前端：Jinja 模板 + 原生 JavaScript
- 数据持久化：`data/app-state.json`
- 实时天气：和风天气 API（仅 `APP_DATA_MODE=live` 时启用）
- 截图：Python Playwright
- 报告生成：Python + `python-docx`

## 题目要求对照

| 原题项目 | 当前实现 | 状态 |
| --- | --- | --- |
| 任务：设计手机端雾霾 app 探测系统 | 使用 HTML5 手机端单页 Web App 实现，手机浏览器访问同一页面即可完成定位和展示 | 已满足 |
| 要求 1：定位城市保存在服务器端，并显示在客户端 | 百度地图 JS API 获取城市，`POST /api/location` 保存到 `data/app-state.json`，首页 Header 显示城市 | 已满足 |
| 要求 2：界面包含天气和空气质量指数动态显示 | 首页 Body 直接展示实时天气、AQI、污染物、体感、湿度、风速、能见度 | 已满足 |
| 要求 3：根据定位城市获取天气详情和 AQI，并保存在服务器端 | 服务端根据保存的城市/经纬度生成 dashboard，`live` 模式调用和风天气 API，结果写入 `data/app-state.json` | 已满足 |
| 要求 4：完成报告 | `scripts/generate_report.py` 生成 `output/doc/雾霾探测系统设计实验报告.docx` | 已满足，个人信息需手动填写 |
| 说明 1：可用百度地图 API 获取定位 | 前端使用百度地图 JS API，精确定位失败时回退 IP 城市定位，并尝试逆地址解析补省份/城市 | 已满足 |
| 说明 2：天气和 AQI 可用和风天气等数据源 | 默认 `mock` 演示；`APP_DATA_MODE=live` 时使用和风天气实时天气、24 小时天气、空气质量 API | 已满足，真实演示需 API Key |
| 说明 3：HTML5 适配手机像素，Header 定位，Body 显示天气/AQI/温湿度折线图 | `viewport` + 响应式 CSS；Header 为定位状态，Body 为天气/AQI/污染物/温湿度折线图 | 已满足 |
| 评价：定位功能 20 分 | 城市、省份、经纬度、定位方式保存并回显 | 已覆盖 |
| 评价：界面设计 20 分 | 单页手机天气 App 风格，信息紧凑，适配小屏 | 已覆盖 |
| 评价：天气空气质量指数 20 分 | 实时天气、AQI、首要污染物、污染物浓度、健康提示、趋势图 | 已覆盖 |
| 评价：编码测试 20 分 | `uv run pytest` 当前 10 个测试通过 | 已覆盖 |
| 报告：方案、结果、规范性 20 分 | 自动生成报告，含问题、方案、数据获取、结果、测试、心得、附录 | 已覆盖，封面需补个人信息 |

提交前需要确认：

- `.env` 中 `BAIDU_MAP_AK` 是有效浏览器端 AK，并配置本机/手机访问地址的 Referer 白名单。
- 如果要演示真实天气数据，把 `APP_DATA_MODE=live`，并填写 `QWEATHER_API_HOST` 和 `QWEATHER_API_KEY`。
- 报告封面的姓名、学号、学院、组号、教师、签名等需要手动填写。

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

- `HOST`
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

如果要在同一 Wi-Fi 下用手机访问，把 `.env` 里的 `HOST` 改成 `0.0.0.0`，重启服务后在手机浏览器打开 `http://电脑局域网IP:3000`。

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
- `output/doc/雾霾探测系统设计实验报告.docx`
