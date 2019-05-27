import json

json_input = '{"items":[{"message":"Hello, world from v1 of Tasks API"}]}'
decoded = None

try:
    decoded = json.loads(json_input)
    print('decoded: {}'.format(decoded))
    print('message: {}'.format(decoded.get('items')[0].get('message')))
except(ValueError, KeyError, TypeError):
    print("JSON format error")
