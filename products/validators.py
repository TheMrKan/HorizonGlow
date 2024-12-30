from rest_framework.exceptions import ValidationError


class DescriptionValidator:
    MAX_LENGTH = 400

    def __init__(self):
        pass

    def __call__(self, value: str):
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(f"Description can't be longer than {self.MAX_LENGTH} characters")
        return value


class NumberValidator:
    MAX_LENGTH = 4
    ALLOWED_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyz"

    def __init__(self):
        pass

    def __call__(self, value: str):
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(f"Number can't be longer than {self.MAX_LENGTH} characters")

        value = value.lower()
        for char in value:
            if char not in self.ALLOWED_CHARACTERS:
                raise ValidationError(f"Number can't contain '{char}' character")
        return value


class ScoreValidator:
    MAX_LENGTH = 2
    ALLOWED_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self):
        pass

    def __call__(self, value: str):
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(f"Score can't be longer than {self.MAX_LENGTH} characters")

        value = value.upper()
        for char in value:
            if char not in self.ALLOWED_CHARACTERS:
                raise ValidationError(f"Score can't contain '{char}' character")
        return value


class PriceValidator:
    MIN_PRICE = 0.1
    MAX_PRICE = 1000

    def __init__(self):
        pass

    def __call__(self, value: float):
        if value < self.MIN_PRICE or value > self.MAX_PRICE:
            raise ValidationError(f"Price is must be between {self.MIN_PRICE}$ and {self.MAX_PRICE}$")
        return value
