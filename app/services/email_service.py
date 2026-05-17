import aiosmtplib
from email.mime.text import MIMEText

from config import settings


class EmailService:
    async def send_order_completed(self, to_email: str, order_id: int) -> None:
        message = MIMEText(
            f"Ваш заказ #{order_id} успешно выполнен. Спасибо, что пользуетесь нашей службой доставки!",
            "plain",
            "utf-8",
        )
        message["From"] = settings.mail.from_address
        message["To"] = to_email
        message["Subject"] = f"Заказ #{order_id} завершён"

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.mail.host,
                port=settings.mail.port,
                start_tls=False,
            )
        except Exception as exc:
            print(f"[EmailService] Ошибка отправки письма на {to_email}: {exc}")
