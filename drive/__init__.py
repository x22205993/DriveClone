import json
def json_loads_suppress_exc(body):
    try:
        body = json.loads(body)
        return body
    except json.JSONDecodeError as e:
        print(e)
    return None
