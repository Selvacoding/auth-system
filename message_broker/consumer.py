import json
import pika

from message_broker.connection import get_connection
from message_broker.topology import (
    MAIN_EXCHANGE,
    RETRY_EXCHANGE,
    DLX_EXCHANGE,
    REGISTRATION_QUEUE,
    REGISTRATION_ROUTING_KEY,
    RETRY_ROUTING_KEY,
    DLQ_ROUTING_KEY,
)

from db.database import (
    is_event_processed,
    mark_event_processed
)

from utils.email import send_registration_email

MAX_RETRIES = 3


def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        event_id = message["event_id"]
        retry_count = message.get("retry_count", 0)
        print(f"Received event: {message}")
        print(f"Attempt: {retry_count + 1}")

        # Idempotency check
        if is_event_processed(event_id):
            print(f"Event {event_id} already processed. Skipping.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"Processing event {event_id}...")

        send_registration_email(to_email=message["email"], username=message["username"])
        mark_event_processed(event_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Event {event_id} processed successfully.")

    except Exception as e:
        print(f"Failed to process event: {e}")
        retry_count = message.get("retry_count", 0)

        if retry_count < MAX_RETRIES:
            retry_message = message.copy()
            retry_message["retry_count"] = retry_count + 1
            print(f"Retrying event {event_id}. Retry count: {retry_message['retry_count']}")

            ch.basic_publish(
                exchange=RETRY_EXCHANGE,
                routing_key=RETRY_ROUTING_KEY,
                body=json.dumps(retry_message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )

        else:
            print(f"Event {event_id} exceeded maximum retries. Sending to DLQ.")
            ch.basic_publish(
                exchange=DLX_EXCHANGE,
                routing_key=DLQ_ROUTING_KEY,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():

    connection = get_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=MAIN_EXCHANGE,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(
        queue=REGISTRATION_QUEUE,
        durable=True,
    )

    channel.queue_bind(
        exchange=MAIN_EXCHANGE,
        queue=REGISTRATION_QUEUE,
        routing_key=REGISTRATION_ROUTING_KEY,
    )

    channel.basic_qos(
        prefetch_count=10
    )

    channel.basic_consume(
        queue=REGISTRATION_QUEUE,
        on_message_callback=callback,
        auto_ack=False,
    )

    print("Registration consumer started...")

    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
