FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYCODE=1 PYTHONUNBUFFEERED=1
COPY pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn[standart] httpx dnspython prometheus-client apscheduler
COPY app /app/app
EXPOSE 8000
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]