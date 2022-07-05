from rest_api_backend_va_project.celery import app
from utils.send_letter_on_email.send_letter_on_email import SendEmail


@app.task(bind=True)
def send_letter_to_email(self, to_email, email_subject, email_body):
    try:
        send_letter = SendEmail(to_email, email_subject, email_body)
        send_letter.send()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=20)
