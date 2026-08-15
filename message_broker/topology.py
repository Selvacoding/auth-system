import pika

from message_broker.connection import get_connection

import CONFIG

MAIN_EXCHANGE = CONFIG.MAIN_EXCHANGE
RETRY_EXCHANGE = CONFIG.RETRY_EXCHANGE
DLX_EXCHANGE = CONFIG.DLQ_EXCHANGE

REGISTRATION_ROUTING_KEY = CONFIG.REGISTRATION_ROUTING_KEY
RETRY_ROUTING_KEY = CONFIG.RETRY_ROUTING_KEY
DLQ_ROUTING_KEY = CONFIG.DLQ_ROUTING_KEY

REGISTRATION_QUEUE = CONFIG.REGISTRATION_QUEUE
RETRY_QUEUE = CONFIG.RETRY_QUEUE
DLQ_QUEUE = CONFIG.DLQ_QUEUE

TTL = CONFIG.RETRY_TTL

def setup_topology():

    connection = get_connection()
    channel = connection.channel()


    channel.exchange_declare(
        exchange=MAIN_EXCHANGE,
        exchange_type="direct",
        durable=True,
    )

    channel.exchange_declare(
        exchange=RETRY_EXCHANGE,
        exchange_type="direct",
        durable=True,
    )

    channel.exchange_declare(
        exchange=DLX_EXCHANGE,
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

    channel.queue_declare(
        queue=RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": TTL,
            "x-dead-letter-exchange": MAIN_EXCHANGE,
            "x-dead-letter-routing-key": REGISTRATION_ROUTING_KEY,
        },
    )

    channel.queue_bind(
        exchange=RETRY_EXCHANGE,
        queue=RETRY_QUEUE,
        routing_key=RETRY_ROUTING_KEY,
    )

    channel.queue_declare(
        queue=DLQ_QUEUE,
        durable=True,
    )

    channel.queue_bind(
        exchange=DLX_EXCHANGE,
        queue=DLQ_QUEUE,
        routing_key=DLQ_ROUTING_KEY,
    )

    print("RabbitMQ topology created successfully.")

    connection.close()


if __name__ == "__main__":
    setup_topology()