import time
import random

from flask import Flask, jsonify, request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "auth-service"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="jaeger:4317", insecure=True))
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

@app.route('/check_auth', methods=['POST'])
def check_auth():
    with tracer.start_as_current_span("authenticate") as span:
        time.sleep(random.randint(1, 4))
        # Dummy authentication - always return True
        auth = random.randint(0, 2)
        if auth < 2:
            return jsonify({"authenticated": True}), 200
        
        return jsonify({"authenticated": False}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)