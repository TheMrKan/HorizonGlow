from bestconfig import Config
from bestconfig.config_provider import ConfigProvider
from typing import Protocol


class GeneralProtocol(Protocol):
    error: str


class UserCommandsProtocol(Protocol):
    start_message: str
    new_ticket_button: str
    new_ticket_answer: str


class ConfigProtocol(Protocol):
    BOT_TOKEN: str
    general: GeneralProtocol
    user_commands: UserCommandsProtocol
    logging: dict


class ConfigInherited(ConfigProvider, ConfigProtocol):
    pass


instance: ConfigInherited = Config()