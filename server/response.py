from flask import Response
import json

def response_json(msg, status):
    return Response(
                    json.dumps(msg),
                    status=status,
                    mimetype='application/json')