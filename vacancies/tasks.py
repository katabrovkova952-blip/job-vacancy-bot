from celery import shared_task


@shared_task
def ping() -> str:
    print('Привіт з Celery!', flush=True)
    return 'pong'