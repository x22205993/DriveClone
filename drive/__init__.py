import json
def json_loads_suppress_exc(body):
    ''' Suppresses the Exception raised because of invalid JSON Object instead returns none'''
    try:
        body = json.loads(body)
        return body
    except json.JSONDecodeError as e:
        print(e)
    return None
