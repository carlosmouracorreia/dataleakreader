import os
import time
from celery import Celery
import celeryconfig
import redis
from datetime import datetime
import json
from celery import group

CONST_META_FILE_CHANGED = 'META-FILE-CHANGED_{file_name}'
CONST_META_FILE_LINE_NR = 'META-FILE-LINES-NR_{file_name}'


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.config_from_object(celeryconfig)

@celery.task(name='tasks.test_me')
def test_me():

    dir_path = os.path.join(os.path.dirname(__file__), '..' , 'data')
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    group(test_me_final.s(file_name) for file_name in files)()

@celery.task(name='tasks.test_me_final')
def test_me_final(file_name):
    file_path = os.path.join(os.path.dirname(__file__), '..' , 'data', file_name)
    leak_name = os.path.splitext(file_name)[0]
    stat = os.stat(file_path)
    str_time = str(datetime.fromtimestamp(stat.st_mtime))

    r = redis.Redis(host='redis', port='6379', db=1, decode_responses=True)

    #in case file hasn't changed since last update
    if r.get(CONST_META_FILE_CHANGED.format(file_name=file_name)) == str_time:
        return

    n_lines_read = 0
    n_processed = 0
    pipe = r.pipeline()
    with open(file_path) as f:

        stored_line_nr = r.get(CONST_META_FILE_LINE_NR.format(file_name=file_name))

        for cnt, line in enumerate(f):

            # pass through already scanned/stored lines/emails
            n_lines_read += 1

          
            if stored_line_nr is not None and int(stored_line_nr) >= n_lines_read:
                continue

            n_processed += 1
            line = line.rstrip('\n')

            # super simple domain discovery - not checking for existing "@" in the email prefix 
            # (not sure how fast it is to regex things)!
            domain = line.split("@")[1] if "@" in line else line
            dict_ = {"email": line, "leak": leak_name}
            dict_ = json.dumps(dict_)
            pipe.lpush('DOMAIN-' + domain, dict_)
            pipe.incr('STAT-EMAIL-NR')
            # do it in a batch fashion
            if (n_processed % 32) == 0:
                pipe.execute()
                pipe = r.pipeline()


        
        
        r.set(CONST_META_FILE_CHANGED.format(file_name=file_name), str_time)
        r.set(CONST_META_FILE_LINE_NR.format(file_name=file_name), n_lines_read)
        pipe.execute()


    print("DID IT! - " + file_name)