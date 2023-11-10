import time
import requests

from flask import Flask, jsonify, request
from pymongo import MongoClient

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# Setup MongoDB client - the hostname will be the service name defined in docker-compose
client = MongoClient("mongodb://mongo:27017/")
db = client.purchase_orders

@app.route('/purchase', methods=['GET'])
def purchase():
    with tracer.start_as_current_span("purchase") as span:
        # Call the auth service
        auth_response = requests.post('http://auth_service:5001/check_auth')
        if auth_response.json().get('authenticated'):
            if check_stock():
                # Write to MongoDB
                order_data = {"order": "dummy_order_info"}  # Replace with actual order data as needed
                db.orders.insert_one(order_data)
                return jsonify({"status": "success", "message": "Order placed."}), 201
        return jsonify({"status": "failure", "message": "Authentication failed."}), 401

@app.route('/orders', methods=['GET'])
def get_orders():
    with tracer.start_as_current_span("orders") as span:
        # Retrieve all orders from MongoDB
        orders = list(db.orders.find({}, {'_id': False}))  # Excluding the default MongoDB '_id' field
        return jsonify(orders), 200

def check_stock():
    with tracer.start_as_current_span("check_stock") as span:
        time.sleep(3)
        # Dummy stock check - always return True for simplicity
        return True


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
