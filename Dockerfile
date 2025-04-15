FROM python:3.9-slim
WORKDIR /app
COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt
COPY . .
RUN mkdir -p /app/logs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]