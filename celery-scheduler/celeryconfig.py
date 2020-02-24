from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'tasks.launch',
        'schedule': timedelta(seconds=int(os.getenv("WORKER_TRIGGER_SECOND_FREQUENCY"))),
    }
}