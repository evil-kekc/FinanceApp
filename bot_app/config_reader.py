import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    """Class for accessing the bot token and admin id"""
    token: str
    admin_id: int
    host_url: str


@dataclass
class Config:
    """A class that generalizes the bot settings into one instance"""
    tg_bot: TgBot


def load_config(path: str):
    """Function to load and read configuration from a text file

    :param path: the path to the file
    :return:
    """
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config['bot']

    return Config(
        tg_bot=TgBot(
            token=tg_bot['token'],
            admin_id=int(tg_bot['admin_id']),
            host_url=tg_bot['host_url']
        )
    )
