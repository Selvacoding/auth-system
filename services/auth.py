from utils.auth import create_user_in_db, login_user, logout_user
class AuthService:
    def register(self, username: str, email: str, password: str):
        return create_user_in_db(username, email, password)

    def login(self, email: str, password: str):
        return login_user(email, password)
    def logout(self, refresh_token: str):
        return logout_user(refresh_token)