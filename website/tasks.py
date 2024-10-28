from celery import shared_task
from flask import current_app
import time
from .models import OTPStore
from celery import current_task
from website import db

# Task 1: Simple Long Running Task
@shared_task
def long_running_task(data):
    time.sleep(10)
    return f"Task completed with data: {data}"

# Task 2: Add OTP to the Database
@shared_task
def add_user(email, otp):
    with current_app.app_context():  # Access Flask app context
        new_user = OTPStore(email=email, otp=otp)
        db.session.add(new_user)
        db.session.commit()
        return f'OTP {otp} added to the database!'

# Task 3: Long Running Task with Retry Logic
@shared_task(bind=True, max_retries=3)
def long_running_task_with_retry(self):
    try:
        time.sleep(5)  # Simulate a long-running process
        return "Long task completed!"
    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # Retry after 60 seconds
