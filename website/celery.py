from celery import Celery
from flask import Flask
from config import Config

def create_celery_app(app: Flask = None):
    app = app or Flask(__name__)
    app.config.from_object(Config)

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    
    return celery

celery_app = create_celery_app()  # This initializes the Celery app
