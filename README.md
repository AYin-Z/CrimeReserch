# 突发公共事件与犯罪研究多源爬虫

该项目聚合新闻、空间、房产与法律文书等多源数据，支撑突发公共事件风险评估与犯罪研究。核心亮点：

- 🧩 模块化核心：`core/` 下的四类爬虫继承统一基类，支持分布式调度与断点续跑。
- 🌐 空间智能：内置 5km×5km 网格化与 WGS84 坐标转换，输出 GeoJSON/PostgreSQL。
- 🔄 数据管线：`data_pipeline.py` 负责去重、校验、规范化并写入数据库。
- 🛡️ 反爬策略：用户代理轮换、指数退避、代理池与频率控制。

## 快速开始

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

配置 `config/crawler_config.yml`（示例见 `config.py` 注释或创建自定义 YAML）。可通过环境变量 `BAIDU_LBS_AK`、`POSTGRES_DSN` 覆盖敏感信息。

## 运行示例

```bash
# 单个任务（默认写入 news_records）
python -m crawler_project.main news --start-date 2015-01-01 --end-date 2015-12-31 --table news_events

# 多任务并发调度（最多 3 个并发）
python -m crawler_project.main news spatial housing --parallelism 3 --postgres-dsn postgresql+psycopg2://user:pwd@host:5432/db

# Scrapy 入口
scrapy crawl north_news -s LOG_LEVEL=INFO
scrapy crawl housing_market -a max_pages=5
```

> Scrapy 位于 `crawler_project/scrapy_app`，其入口文件 `scrapy.cfg` 已配置完成，可在 `crawler_project/` 目录下直接运行 `scrapy crawl <spider_name>`。

### PostgreSQL 连接

- 默认 DSN 为 `config.py` / `config/crawler_config.yml` 中的 `storage.postgres_dsn`。
- 运行 CLI 时可使用 `--postgres-dsn` 临时覆盖。
- 连接池参数（`pool_size`、`max_overflow`、`pool_timeout`）也可在配置文件中调整。

## 自动化测试

```bash
pytest
```

## 目录结构

```
crawler_project/
├── core/                # 各类爬虫实现
├── utils/               # 配置、代理、解析、存储工具
├── scrapy_app/          # Scrapy 项目（spiders、pipelines、settings）
├── data_pipeline.py     # 数据标准化与写入
├── main.py              # 命令行入口
├── logs/                # 运行日志
├── output/              # 输出文件
└── requirements.txt
```

## 注意事项

- 严格遵守目标网站 robots.txt 与 API 速率限制。
- 新闻/法律爬虫默认延迟 ≥2s；API 任务根据平台限流调度。
- 敏感字段在入库前调用脱敏逻辑（可在 `data_pipeline` 中扩展）。
- 使用代理池前，在 `utils/proxy_manager.py` 配置地址并启用 `config.ProjectSettings.proxy`。
