from flask import Flask
from flask import url_for
import redis
import json
import os

app = Flask(__name__)

@app.route('/send')
def send():
    r = redis.Redis(host='redis', port='6379', db=1)

    n = 1
    pipe = r.pipeline()
    with open(os.path.join(os.path.dirname(__file__), 'test.txt')) as f:
        for cnt, line in enumerate(f):
            # super simple domain discovery - not checking for existing "@" in the email prefix 
            # (not sure how fast it is to regex things)!
            domain = line.split("@")[1]
            pipe.lpush(domain, {"email": line})
            n = n + 1
            # do it in a batch fashion
            if (n % 32) == 0:
                pipe.execute()
                pipe = r.pipeline()
    return str('Did it!')

@app.route('/get')
def get():
    r = redis.Redis(host='redis',port='6379', db=1, decode_responses=True)
    dict_ = []

    for key in r.keys():
        dict__ = []
        for value in r.lrange(key,0,-1):
            dict__.append(value)
        dict_.append({"domain": key, "data": dict__})
    return json.dumps(dict_)