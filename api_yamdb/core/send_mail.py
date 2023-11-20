from django.core import mail


def send_mail(from_email, to_email, subject, message):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            subject, message, from_email, [to_email],
            connection=connection,
        ).send()
