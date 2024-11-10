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

    def update_credentials(self, commit=True):
        self.user.set_password(self.password)
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



