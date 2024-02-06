from loguru import logger

from config.server import server_settings


logger.add('logs/debug.json', level=server_settings.LOG_LEVEL, rotation='5 MB', compression='zip', serialize=True)
logger.opt(exception=True)
