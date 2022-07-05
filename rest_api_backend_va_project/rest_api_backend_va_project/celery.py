import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest_api_backend_va_project.settings')

app = Celery('my_va_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
