from .models import User


class UserCredentialsManager:
    user: User
    password: str | None
    secret_phrase: str | None

    def __init__(self, user: User, password: str | None, secret_phrase: str | None):
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

    def check_credentials_partial(self) -> (bool, bool):
        """
        Сравнивает переданные данные с сохраненными в БД.
        В отличие от check_credentials, сравниваться будут только not-None поля
        :return:
        """
        password_valid = True
        if self.password is not None:
            if not self.user.check_password(self.password):
                password_valid = False

        phrase_valid = True
        if self.secret_phrase is not None:
            if self.user.secret_phrase:
                phrase_valid = self.user.secret_phrase.casefold() == self.secret_phrase.casefold()

        return password_valid, phrase_valid

    def update_credentials(self, commit=True, partial=True):
        if not partial or self.password:
            self.user.set_password(self.password)

        if not partial or self.secret_phrase:
            self.user.secret_phrase = self.secret_phrase.casefold()

        if commit:
            self.user.save()


class UserCreator:
    username: str
    password: str
    secret_phrase: str

    def __init__(self, username: str, password: str, secret_phrase: str):
        self.username = username
        self.password = password
        self.secret_phrase = secret_phrase

    def is_user_exists(self):
        return User.objects.filter(username=self.username).exists()

    def create(self) -> User:
        if self.is_user_exists():
            raise ValueError(f'User {self.username} already exists')

        user = User(username=self.username)
        UserCredentialsManager(user, self.password, self.secret_phrase).update_credentials(commit=False)
        user.save()

        return user



