from flask import Flask
from flask import url_for
import redis
import json
import os
from flask import request
from flask import jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/info')
def info():
    type_ = request.args.get('type')
    query = request.args.get('query')

    if not query or not query.strip():
        return jsonify({"error": "missing query parameter"}), 400

    if type_ != "email" and type_ != "domain":
        return jsonify({"error": "type query parameter as either email or domain"}), 400

    r = redis.Redis(host='redis_leaks',port='6379', db=1, decode_responses=True)

    if type_ == "domain":
        domain_data = r.lrange('DOMAIN-' + str(query), 0,-1)
        # redis json-string list needs to be converted to json (deserialized) list in order to be unserialized
        domain_data = [json.loads(ob) for ob in domain_data]
        return jsonify({ 'total_email_nr': r.get('STAT-EMAIL-NR'), 'emails': domain_data})
    
    if type_ == "email":
        email_data = r.lrange('EMAIL-' + str(query), 0,-1)
        return jsonify({ 'total_email_nr': r.get('STAT-EMAIL-NR'), 'leaks': email_data})



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