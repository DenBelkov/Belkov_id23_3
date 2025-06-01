from celery import Celery

celery_app = Celery(
    'app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['app.services']
)


celery_app.conf.update(
    worker_concurrency=2,
    task_annotations={
        '*': {'rate_limit': '100/s'}
    }
)
