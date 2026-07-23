from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey
)

import CONFIG

DATABASE_URL = f"postgresql://{CONFIG.POSTGRES_USER}:{CONFIG.POSTGRES_PASSWORD}@{CONFIG.POSTGRES_HOST}:{CONFIG.POSTGRES_PORT}/{CONFIG.POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)

meta = MetaData()
ist = ZoneInfo("Asia/Kolkata")


users = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(ist)
    )
)


refresh_tokens = Table(
    "refresh_tokens",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False
    ),
    Column("token", String, nullable=False, unique=True),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("revoked", Boolean, default=False, nullable=False)
)


def get_user_by_email(email: str):
    with engine.connect() as connection:
        query = users.select().where(users.c.email == email)
        result = connection.execute(query).fetchone()
        print("Email searched:", email)
        print("Query result:", result)
        return result


def create_user(username: str, email: str, password: str):
    with engine.connect() as connection:
        query = users.insert().values(
            username=username,
            email=email,
            password=password
        )
        connection.execute(query)
        connection.commit()


def save_refresh_token(user_id: int, token: str, expires_at):
    with engine.connect() as connection:
        query = refresh_tokens.insert().values(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False
        )
        connection.execute(query)
        connection.commit()


def revoke_refresh_token(refresh_token: str):
    with engine.connect() as connection:
        query = (
            refresh_tokens.update()
            .where(refresh_tokens.c.token == refresh_token)
            .values(revoked=True)
        )

        result = connection.execute(query)
        connection.commit()

        return result