import logging
from json import loads
from pathlib import Path

from bot.bot_client import BotClient

HERE = Path(Path(__file__).parent)


class ColouredFormatter(logging.Formatter):
    def __init__(self, colours=None, fmt=None, datefmt=None, style='%'):
        self.colours = colours or {}
        self.reset = '\x1b[0m'
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        res = super().format(record)
        colour = self.colours.get(record.levelno)
        if colour:
            return f'{colour}{res}{self.reset}'
        return res


def setup_logging():
    formatter = ColouredFormatter(
        colours={
            logging.INFO: '\x1b[36m',  # Cyan
            logging.WARNING: '\x1b[33m',  # Yellow
            logging.ERROR: '\x1b[31m',  # Red
            logging.CRITICAL: '\x1b[35m'  # Purple
        },
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('matrix_client')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger


def main(user, passw, rooms):
    client = BotClient('https://matrix.org', setup_logging())
    client.start(user, passw, rooms)


if __name__ == '__main__':
    conf = loads(HERE.joinpath('conf').joinpath('conf.json').read_text())
    main(conf['username'], conf['password'], conf['rooms'])
