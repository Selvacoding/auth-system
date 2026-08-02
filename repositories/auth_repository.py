from datetime import datetime

from db.database import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    save_refresh_token,
    rotate_refresh_token,
    revoke_refresh_token
)


class AuthRepository:

    def get_user_by_email(self, email: str):
        return get_user_by_email(email)

    def get_user_by_id(self, user_id: int):
        return get_user_by_id(user_id)

    def create_user(self, username: str, email: str, password: str):
        return create_user(username, email, password)

    def save_refresh_token(self, user_id: int, token: str, expires_at: datetime):
        return save_refresh_token(user_id, token, expires_at)

    def rotate_refresh_token(self, user_id: int, old_refresh_token: str,
                                new_refresh_token: str,
                                expires_at: datetime
                            ):
        return rotate_refresh_token(user_id, old_refresh_token, new_refresh_token, expires_at)

    def revoke_refresh_token(self, user_id: int, refresh_token: str):
        return revoke_refresh_token(user_id, refresh_token)
