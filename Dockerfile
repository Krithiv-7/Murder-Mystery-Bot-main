FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:///data/bot.sqlite \
    MMB_STORAGE=sqlite

WORKDIR /app

RUN useradd --create-home --uid 1000 bot \
    && mkdir -p /app/data /app/backups /app/logs \
    && chown -R bot:bot /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=bot:bot . .

USER bot

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD ["python", "-m", "core.cli", "health"]

CMD ["python", "bot.py"]
