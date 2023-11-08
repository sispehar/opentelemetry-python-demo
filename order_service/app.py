from flask import Flask, jsonify, request
import requests
from pymongo import MongoClient

app = Flask(__name__)

# Setup MongoDB client - the hostname will be the service name defined in docker-compose
client = MongoClient("mongodb://mongo:27017/")
db = client.purchase_orders

@app.route('/purchase', methods=['GET'])
def purchase():
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
    # Retrieve all orders from MongoDB
    orders = list(db.orders.find({}, {'_id': False}))  # Excluding the default MongoDB '_id' field
    return jsonify(orders), 200

def check_stock():
    # Dummy stock check - always return True for simplicity
    return True


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
