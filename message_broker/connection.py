import pika
import CONFIG


RABBITMQ_HOST = CONFIG.RABBITMQ_HOST
RABBITMQ_PORT = CONFIG.RABBITMQ_PORT
RABBITMQ_USERNAME = CONFIG.RABBITMQ_USERNAME
RABBITMQ_PASSWORD = CONFIG.RABBITMQ_PASSWORD


def get_connection():
    credentials = pika.PlainCredentials(
        RABBITMQ_USERNAME,
        RABBITMQ_PASSWORD,
    )

    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
    )

    return pika.BlockingConnection(parameters)
