from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/check_auth', methods=['POST'])
def check_auth():
    # Dummy authentication - always return True
    return jsonify({"authenticated": True}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)