FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SJTU_AGENT_HOME=/data/sjtu-agent

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt README.md ./
COPY sjtu_agent ./sjtu_agent
COPY agent.py care_check.py daily_report.py ddl_checker.py login.py mcp_server.py news_digest.py remind_check.py setup_config.py shuiyuan_watcher.py telegram_bot.py wechat_bot.py ./

RUN python -m pip install --upgrade pip \
    && python -m pip install -e . \
    && python -m playwright install --with-deps chromium

EXPOSE 8765

CMD ["sjtu-agent", "mcp", "--http", "--host", "0.0.0.0", "--port", "8765"]
