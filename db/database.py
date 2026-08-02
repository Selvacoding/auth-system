from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    ForeignKey
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
    echo=True
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



def create_user(username: str, email: str, password: str):
    with Session(engine) as session:
        user = User(username=username, email=email, password=password)
        session.add(user)
        session.commit()

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
