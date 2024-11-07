from .models import User


class UserCredentialsManager:
    user: User
    password: str
    secret_phrase: str

    def __init__(self, user: User, password: str, secret_phrase: str):
        self.user = user
        self.password = password
        self.secret_phrase = secret_phrase

    def check_credentials(self) -> bool:
        """
        Сравнивает переданные данные с сохраненными в БД
        :return: True, если данные совпадают; иначе False
        """
        if not self.user.check_password(self.password):
            return False

        if not self.user.secret_phrase:
            return True

        if not self.secret_phrase:
            return False

        return self.user.secret_phrase.casefold() == self.secret_phrase.casefold()
