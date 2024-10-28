class Config:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis broker
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Redis backend
