import time
import requests
import random

from flask import Flask, jsonify, request
from pymongo import MongoClient
from faker import Faker

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "order-service"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="jaeger:4317", insecure=True))
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# Setup MongoDB client - the hostname will be the service name defined in docker-compose
client = MongoClient("mongodb://mongo:27017/")
db = client.purchase_orders
fake = Faker()

@app.route('/purchase', methods=['GET'])
def purchase():
    with tracer.start_as_current_span("purchase") as span:
        # Call the auth service
        user = fake.free_email()
        auth_response = requests.post(f'http://auth_service:5001/check_auth?user={user}')
        if auth_response.json().get('authenticated'):
            if check_stock():
                time.sleep(random.randint(1, 4))
                # Write to MongoDB
                order_id = random.randint(1, 99)
                order_data = {"order_id": order_id, "user": user}
                db.orders.insert_one(order_data)

                # OpenTelemetry attributes
                span.set_attribute("order.id", order_id)
                span.set_attribute("order.user", user)
                span.add_event("order succesful")

                return jsonify({"status": "success", "message": "Order placed."}), 201
        
        span.add_event(f"order failed {user}")
        span.set_status(Status(StatusCode.ERROR))

        return jsonify({"status": "failure", "message": "Authentication failed."}), 401

@app.route('/orders', methods=['GET'])
def get_orders():
    with tracer.start_as_current_span("orders") as span:
        # Retrieve all orders from MongoDB
        orders = list(db.orders.find({}, {'_id': False}))  # Excluding the default MongoDB '_id' field
        return jsonify(orders), 200

def check_stock():
    with tracer.start_as_current_span("check_stock") as span:
        time.sleep(random.randint(4, 12))
        # Dummy stock check - always return True for simplicity
        return True


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
