from flask import request

def create_data(request):
    req_type = request.content_type
    if 'form' in req_type:
        return request.form
    elif 'json' in req_type:
        return request.get_json()
    else:
        return request.args