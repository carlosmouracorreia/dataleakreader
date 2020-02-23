from flask import Flask
from flask import url_for
import redis
import json
import os
from flask import request
from flask import jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/send')
def send():
    r = redis.Redis(host='redis', port='6379', db=1)

    n = 1
    pipe = r.pipeline()
    file_path = os.path.join(os.path.dirname(__file__), 'test.txt')
    with open(file_path) as f:
        stat = os.stat(file_path)
        str_time = datetime.fromtimestamp(stat.st_mtime)
        r.set('META-FILE-CHANGED', str(str_time))

        for cnt, line in enumerate(f):
            line = line.rstrip('\n')
            # super simple domain discovery - not checking for existing "@" in the email prefix 
            # (not sure how fast it is to regex things)!
            domain = line.split("@")[1] if "@" in line else line
            dict_ = {"email": line}
            dict_ = json.dumps(dict_)
            pipe.lpush('DOMAIN-' + domain, dict_)
            pipe.incr('EMAILNR')
            n = n + 1
            # do it in a batch fashion
            if (n % 32) == 0:
                pipe.execute()
                pipe = r.pipeline()
    return str('Did it!')

@app.route('/info')
def info():
    domain = request.args.get('domain')

    r = redis.Redis(host='redis',port='6379', db=1, decode_responses=True)
    domain_data = r.lrange('DOMAIN-' + str(domain), 0,-1)

    return jsonify({ 'changed': r.get('META-FILE-CHANGED') , 'total_email_nr': r.get('EMAILNR'), 'domain_email_nr_pag': '0', 'emails': domain_data})

@app.route('/get')
def get():
    r = redis.Redis(host='redis',port='6379', db=1, decode_responses=True)
    dict_ = []

    for key in r.keys():
        if not "DOMAIN-" in key:
            continue
        dict__ = []
        for value in r.lrange(key,0,-1):
            dict__.append(json.loads(value))
        dict_.append({"domain": key, "data": dict__})
    return json.dumps(dict_)