from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()


#CELERY_IMPORTS = ('app.tasks.test')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'tasks.launch',
        # Every minute
        'schedule': timedelta(seconds=int(os.getenv("WORKER_TRIGGER_SECOND_FREQUENCY"))),
    }
}