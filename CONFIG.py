import os

POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 3))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

REDIS_HOST = os.getenv("REDIS_HOST", "")
REDIS_PORT = int(os.getenv("REDIS_PORT", ""))

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", ""))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_DEFAULT_USER", "")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASS", "")

MAIN_EXCHANGE = os.getenv("MAIN_EXCHANGE", "")
RETRY_EXCHANGE = os.getenv("RETRY_EXCHANGE", "")
DLX_EXCHANGE = os.getenv("DLX_EXCHANGE", "")

REGISTRATION_ROUTING_KEY = os.getenv("REGISTRATION_ROUTING_KEY", "")
RETRY_ROUTING_KEY = os.getenv("RETRY_ROUTING_KEY", "")
DLQ_ROUTING_KEY = os.getenv("DLQ_ROUTING_KEY", "")

REGISTRATION_QUEUE = os.getenv("REGISTRATION_QUEUE", "")
RETRY_QUEUE = os.getenv("RETRY_QUEUE", "")
DLQ_QUEUE = os.getenv("DLQ_QUEUE", "")

RETRY_TTL = int(os.getenv("RETRY_TTL", ""))

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", ""))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
