FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask opentelemetry-api opentelemetry-sdk
EXPOSE 5001
CMD ["python", "app.py"]