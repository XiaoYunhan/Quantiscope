import logging
from typing import Final, Optional

from twilio.rest import Client

from .config import TWILIO_FROM, TWILIO_SID, TWILIO_TO, TWILIO_TOKEN, USE_VOICE

log = logging.getLogger("notifier")


class Notifier:
    _client: Optional[Client] = None

    @classmethod
    def _get_client(cls) -> Client:
        """Lazy initialization of Twilio client"""
        if cls._client is None:
            if not TWILIO_SID or not TWILIO_TOKEN:
                raise ValueError(
                    "Twilio credentials not configured. Please set TWILIO_SID and TWILIO_TOKEN in your .env file"
                )
            cls._client = Client(TWILIO_SID, TWILIO_TOKEN)
        return cls._client

    @classmethod
    def test_credentials(cls) -> bool:
        """Test if Twilio credentials are valid"""
        try:
            client = cls._get_client()
            # Try to fetch account info to validate credentials
            account = client.api.accounts(TWILIO_SID).fetch()
            log.info(f"Twilio account validated: {account.friendly_name}")
            return True
        except Exception as e:
            log.error(f"Twilio credential test failed: {e}")
            return False

    @classmethod
    def send(cls, text: str, test_mode: bool = False) -> bool:
        """Send notification via SMS or voice call"""
        try:
            if test_mode:
                log.info(f"TEST MODE: Would send notification: {text[:100]}...")
                return True

            if not TWILIO_FROM or not TWILIO_TO:
                raise ValueError(
                    "Twilio phone numbers not configured. Please set TWILIO_FROM and TWILIO_TO in your .env file"
                )

            client = cls._get_client()

            if USE_VOICE:
                # Clean text for voice call (remove emojis and special characters)
                clean_text = text.replace("🚨", "Alert: ").replace("\n", ". ")
                call = client.calls.create(
                    twiml=f"<Response><Say voice='alice' rate='slow'>{clean_text}</Say></Response>",
                    from_=TWILIO_FROM,
                    to=TWILIO_TO,
                )
                log.info(f"Voice call initiated: {call.sid}")
            else:
                message = client.messages.create(
                    body=text[:1600],  # SMS character limit
                    from_=TWILIO_FROM,
                    to=TWILIO_TO,
                )
                log.info(f"SMS sent: {message.sid}")

            return True

        except Exception as e:
            log.error(f"Failed to send notification: {e}")
            return False
