import json

def readjson(filename):
    with open(filename, 'r') as f:
        return json.load(f)