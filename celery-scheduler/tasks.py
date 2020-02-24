import os
import time
from celery import Celery
import celeryconfig
import redis
from datetime import datetime
import json
from celery import group

CONST_META_FILE_CHANGED = 'META-FILE-CHANGED_{leak_name}'
CONST_META_FILE_LINE_NR = 'META-FILE-LINES-NR_{leak_name}'
CONST_META_FILE_RUNNING_TASK = 'META-FILE-TASK-RUNNING_{leak_name}'


CELERY_URL = 'redis://redis_celery:6379'

celery = Celery('tasks', broker=CELERY_URL, backend=CELERY_URL)
celery.config_from_object(celeryconfig)

@celery.task(name='tasks.launch')
def launch():

    dir_path = os.path.join(os.path.dirname(__file__), '..' , 'data')
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    group(read_file.s(file_name) for file_name in files)()

@celery.task(name='tasks.read_file')
def read_file(file_name):

    file_path = os.path.join(os.path.dirname(__file__), '..' , 'data', file_name)
    leak_name = os.path.splitext(file_name)[0]
    r = redis.Redis(host='redis_leaks', port='6379', decode_responses=True)
    # in case there's a task running already to write this data
    if r.get(CONST_META_FILE_RUNNING_TASK.format(leak_name=leak_name)) == 1:
       return
    
    #in case file hasn't changed since last update
    stat = os.stat(file_path)
    str_time = str(datetime.fromtimestamp(stat.st_mtime))
    if r.get(CONST_META_FILE_CHANGED.format(leak_name=leak_name)) == str_time:
        return

    n_lines_read = 0
    n_processed = 0
    pipe = r.pipeline()

    with open(file_path, encoding="utf8", errors="ignore") as f:

        # set running flag so that celery periodic task don't re-do efforts and duplicate data!!
        r.set(CONST_META_FILE_RUNNING_TASK.format(leak_name=leak_name), 1)

        stored_line_nr = r.get(CONST_META_FILE_LINE_NR.format(leak_name=leak_name))

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
            dict_for_domain_key = {"email": line, "leak": leak_name}
            dict_for_domain_key = json.dumps(dict_for_domain_key)
            pipe.lpush('DOMAIN-' + domain, dict_for_domain_key)

            pipe.lpush('EMAIL-' + line, leak_name)

            pipe.incr('STAT-EMAIL-NR')
            # do it in a batch fashion
            if (n_processed % int(os.getenv("BATCH_SIZE_WRITE"))) == 0:
                pipe.execute()
                pipe = r.pipeline()


        
        # execute any missing batch of data to store
        pipe.execute()
        r.set(CONST_META_FILE_CHANGED.format(leak_name=leak_name), str_time)
        r.set(CONST_META_FILE_LINE_NR.format(leak_name=leak_name), n_lines_read)

        # set running flag to 0 so celery periodic tasks can take over
        r.set(CONST_META_FILE_RUNNING_TASK.format(leak_name=leak_name), 0)