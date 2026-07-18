FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY requirements-ai.txt .
ARG INSTALL_AI=false
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt \
    && if [ "$INSTALL_AI" = "true" ]; then \
         pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.1 torchvision==0.22.1 \
         && pip install -r requirements-ai.txt; \
       fi

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

