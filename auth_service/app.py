import time

from flask import Flask, jsonify, request

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

@app.route('/check_auth', methods=['POST'])
def check_auth():
    with tracer.start_as_current_span("authenticate") as span:
        # Dummy authentication - always return True
        return jsonify({"authenticated": True}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)