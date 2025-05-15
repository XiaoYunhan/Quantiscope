from twilio.rest import Client
from typing import Final
from .config import TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TWILIO_TO, USE_VOICE

class Notifier:
    _client: Final[Client] = Client(TWILIO_SID, TWILIO_TOKEN)

    @classmethod
    def send(cls, text: str) -> None:
        if USE_VOICE:
            cls._client.calls.create(
                twiml=f"<Response><Say>{text}</Say></Response>",
                from_=TWILIO_FROM, to=TWILIO_TO
            )
        else:
            cls._client.messages.create(
                body=text, from_=TWILIO_FROM, to=TWILIO_TO
            )
