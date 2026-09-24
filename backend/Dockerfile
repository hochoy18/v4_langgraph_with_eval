FROM python:3.11-slim

# 系统依赖（weasyprint / pandoc）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libffi-dev \
    pandoc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 uv
RUN pip install --no-cache-dir uv

# 依赖
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

# 代码
COPY app ./app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]