import json
import pika

from message_broker.connection import get_connection
from message_broker.topology import (
    MAIN_EXCHANGE,
    REGISTRATION_ROUTING_KEY,
)


def publish_event(event_id: int, event_type: str, payload: dict):
    connection = get_connection()
    channel = connection.channel()
    
    channel.exchange_declare(
        exchange=MAIN_EXCHANGE,
        exchange_type="direct",
        durable=True,
    )

    routing_key = REGISTRATION_ROUTING_KEY

    message = {
        "event_id": event_id,
        "event": event_type,
        **payload
    }

    channel.basic_publish(
        exchange=MAIN_EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
        ),
    )

    print(f"Published: {message}")

    connection.close()
