FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask pymongo requests Faker \
    opentelemetry-api opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-grpc
EXPOSE 5000
CMD ["python", "app.py"]