from flask import Flask
from flask import url_for
import redis
import json
import os
from flask import request
from flask import jsonify
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


CONST_QUERY_TYPE_BY_DOMAIN = 'emails_leaks_from_domain'
CONST_QUERY_TYPE_BY_EMAIL = 'leaks_from_email'

def give_nr(query_param, default=0, max_=False):
    '''
    Return a valid number for limit/offset query parameters in case they're fed by the user
    
    @param: default The default to be enforced
    @param: max_ if the default parameter should also be the maximum allowed
    '''
    nr = int(query_param) if query_param and query_param.isdigit() else default
    return min(nr,default) if max_ else nr

@app.route('/info')
def info():
    '''
    Only endpoint to fetch email data from the in-mem Redis DB. Check README for parameter usage
    '''
    
    type_ = request.args.get('type')
    query = request.args.get('query')
    limit = give_nr(request.args.get('limit'), int(os.getenv("MAX_LIMIT_OUTPUT")), True)
    offset = give_nr(request.args.get('offset'),0)

    if not query or not query.strip():
        return jsonify({"error": "missing query parameter"}), 400

    if type_ != CONST_QUERY_TYPE_BY_DOMAIN and type_ != CONST_QUERY_TYPE_BY_EMAIL:
        return jsonify({"error": f"type query parameter as either {CONST_QUERY_TYPE_BY_DOMAIN} or {CONST_QUERY_TYPE_BY_EMAIL}"}), 400

    r = redis.Redis(host='redis_leaks',port='6379', decode_responses=True)

    if type_ == CONST_QUERY_TYPE_BY_DOMAIN:
        key = f'DOMAIN-{str(query)}'
        data = r.lrange(key, offset,limit + 1)
        # redis json-string list needs to be converted to json (deserialized) list in order to be unserialized
        data = [json.loads(ob) for ob in data]
    
    elif type_ == CONST_QUERY_TYPE_BY_EMAIL:
        key = f'EMAIL-{str(query)}'
        data = r.lrange(key, offset,limit + 1)

    return jsonify({ 'pagination': { 'element_nr': r.llen(key), 'limit': limit, 'offset': offset },\
         'total_email_nr': r.get('STAT-EMAIL-NR'), type_: data})