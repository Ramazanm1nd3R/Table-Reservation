from django.core.mail import EmailMessage
import threading
import logging

logger = logging.getLogger("email")

class EmailThread(threading.Thread):
    """Асинхронная отправка email"""
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send()
            logger.debug("Email sent successfully to %s", self.email.to)
        except Exception as e:
            logger.error("Failed to send email to %s: %s", self.email.to, e)

class Util:
    """Класс для отправки email"""
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=data["to_email"]
        )
        EmailThread(email).start()

def send_activation_email(user, request):
    """Генерирует ссылку активации и отправляет email"""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.urls import reverse
    from .utils import Util  # Убеждаемся, что Util импортирован

    token = default_token_generator.make_token(user)  # Генерируем токен
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Кодируем ID пользователя
    link = request.build_absolute_uri(reverse("activate", args=[uid, token]))  # Формируем ссылку
    subject = "Активируйте ваш аккаунт"
    message = f"Перейдите по ссылке для активации: {link}"

    data = {
        "email_subject": subject,
        "email_body": message,
        "to_email": [user.email],
    }

    Util.send_email(data)  # Отправляем письмо
