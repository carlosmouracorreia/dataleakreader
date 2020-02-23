import os
import time
from celery import Celery
import celeryconfig
import redis
from datetime import datetime


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.config_from_object(celeryconfig)

@celery.task(name='tasks.test_me')
def test_me():
    r = redis.Redis(host='redis', port='6379', db=1)

    n = 1
    pipe = r.pipeline()
    file_path = os.path.join(os.path.dirname(__file__), '../data/test.txt')
    with open(file_path) as f:
        stat = os.stat(file_path)
        str_time = datetime.fromtimestamp(stat.st_mtime)
        r.set('META-FILE-CHANGED', str_time)

        for cnt, line in enumerate(f):
            line = line.rstrip('\n')
            # super simple domain discovery - not checking for existing "@" in the email prefix 
            # (not sure how fast it is to regex things)!
            domain = line.split("@")[0] if "@" in line else line
            pipe.lpush('DOMAIN-' + domain, {"email": line})
            pipe.incr('EMAILNR')
            n = n + 1
            # do it in a batch fashion
            if (n % 32) == 0:
                pipe.execute()
                pipe = r.pipeline()
            print("DID IT!")