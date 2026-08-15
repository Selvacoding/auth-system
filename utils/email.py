import smtplib
from email.message import EmailMessage

import CONFIG


def send_registration_email(to_email: str, username: str):

    message = EmailMessage()

    message["Subject"] = "Welcome to our platform"
    message["From"] = CONFIG.EMAIL_FROM
    message["To"] = to_email

    message.set_content(
        f"""
            Hi {username},

            Welcome! Your account has been successfully created.

            Thanks,
            Auth Service
        """
    )

    with smtplib.SMTP(CONFIG.SMTP_HOST, CONFIG.SMTP_PORT) as server:
        server.starttls()

        server.login(
            CONFIG.SMTP_USERNAME,
            CONFIG.SMTP_PASSWORD
        )

        server.send_message(message)

    print(f"Registration email sent to {to_email}")
    