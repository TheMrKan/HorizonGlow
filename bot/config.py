from bestconfig import Config
from bestconfig.config_provider import ConfigProvider

from bestconfig.file_parsers import YamlParser
import yaml
import warnings

from typing import Protocol


class GeneralProtocol(Protocol):
    error: str


class NewTicketProtocol(Protocol):
    button: str
    answer: str
    no_code: str
    invalid_code: str
    preriod_expired: str
    success: str
    already_have: str


class TicketProtocol(Protocol):
    close_button: str


class CloseTicketProtocol(Protocol):
    closed_message: str


class UserCommandsProtocol(Protocol):
    start_message: str
    message_no_ticket: str
    new_ticket: NewTicketProtocol
    ticket: TicketProtocol
    close_ticket: CloseTicketProtocol


class SupportCommandsProtocol(Protocol):
    pass


class ConfigProtocol(Protocol):
    BOT_TOKEN: str
    API_USERNAME: str
    API_PASSWORD: str
    API_SECRET_PHRASE: str
    DATABASE_URL: str
    SUPPORT_GROUP_ID: int

    base_api_url: str
    general: GeneralProtocol
    user_commands: UserCommandsProtocol
    support_commands: SupportCommandsProtocol
    logging: dict


class ConfigInherited(ConfigProvider, ConfigProtocol):
    pass


# нужно для корректной загрузки эмодзи из yaml конфига
# отличается от оригинала добавлением 'encoding="utf-8"' в параметры open
def read_patch(filepath: str):
    with open(filepath, 'r', encoding="utf-8") as file:
        try:
            data_dict = yaml.load(file, Loader=yaml.Loader)
            if not isinstance(data_dict, dict):
                warnings.warn(f"Error parsing file: {filepath}", SyntaxWarning)
            return data_dict or {}
        except yaml.YAMLError:
            raise SyntaxError
YamlParser.read = read_patch


instance: ConfigInherited = Config()