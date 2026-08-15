from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)

import CONFIG


DATABASE_URL = (
    f"postgresql://"
    f"{CONFIG.POSTGRES_USER}:"
    f"{CONFIG.POSTGRES_PASSWORD}@"
    f"{CONFIG.POSTGRES_HOST}:"
    f"{CONFIG.POSTGRES_PORT}/"
    f"{CONFIG.POSTGRES_DB}"
)


engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=1800,
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  default=lambda: datetime.now(timezone.utc), 
                                                  nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                    default=lambda: datetime.now(timezone.utc),
                                                    nullable=False)


def create_user(username: str, email: str, password: str):
    with Session(engine) as session:
        user = User(username=username, email=email, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user_by_email(email: str):
    with Session(engine) as session:
        user = session.query(User).filter(User.email == email).first()
        return user

def get_user_by_id(user_id: int):
    with Session(engine) as session:
        user = (
            session.query(User)
            .filter(User.id == user_id)
            .first()
        )

        return user

def save_refresh_token(user_id: int, token: str, expires_at: datetime):
    with Session(engine) as session:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False
        )

        session.add(refresh_token)
        session.commit()

def rotate_refresh_token(user_id: int, old_refresh_token: str, new_refresh_token: str, expires_at: datetime):
    with Session(engine) as session:
        token = (
            session.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.token == old_refresh_token,
                RefreshToken.revoked == False
            )
            .first()
        )

        if token is None:
            return False
        token.revoked = True

        new_token = RefreshToken(
            user_id=user_id,
            token=new_refresh_token,
            expires_at=expires_at,
            revoked=False
        )
        session.add(new_token)
        session.commit()

        return True

def revoke_refresh_token(user_id: int, refresh_token: str):
    with Session(engine) as session:
        token = (
            session.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False
            )
            .first()
        )

        if token is None:
            return False
        token.revoked = True
        session.commit()

        return True

def create_user_with_outbox(username: str, email: str, password: str):
    with Session(engine) as session:
        user = User(username=username, email=email, password=password)
        session.add(user)
        session.flush()

        payload={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                }
        event = OutboxEvent(event_type="user.registered", payload=payload)

        session.add(event)
        session.commit()    
        session.refresh(user)
        return user

def get_unpublished_events():
    with Session(engine) as session:
        events = (
            session.query(OutboxEvent)
            .filter(OutboxEvent.published == False)
            .order_by(OutboxEvent.id)
            .all()
        )

        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "payload": event.payload
            }
            for event in events
        ]

def mark_event_as_published(event_id: int):
    with Session(engine) as session:
        event = (
            session.query(OutboxEvent)
            .filter(OutboxEvent.id == event_id)
            .first()
        )

        if event is None:
            return False

        event.published = True
        session.commit()

        return True

def mark_event_processed(event_id: int):
    with Session(engine) as session:
        event = ProcessedEvent(
            event_id=event_id
        )

        session.add(event)
        session.commit()

def is_event_processed(event_id: int):
    with Session(engine) as session:
        event = (
            session.query(ProcessedEvent)
            .filter(
                ProcessedEvent.event_id == event_id
            )
            .first()
        )

        return event is not None
