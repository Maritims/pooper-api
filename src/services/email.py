from logging import getLogger

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.client import Response
from python_http_client.exceptions import HTTPError

log = getLogger(__name__)


class EmailService:
    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    def send_email(self, from_email_address: str, to_email_address: str, subject: str, message: str) -> bool:
        message = Mail(
            from_email=from_email_address,
            to_emails=to_email_address,
            subject=subject,
            html_content=message
        )

        sendgrid_client = SendGridAPIClient(self.api_key)
        response: Response

        try:
            response = sendgrid_client.send(message)
        except HTTPError as err:
            log.error(err.body)
            return False

        return response.status_code == 202
