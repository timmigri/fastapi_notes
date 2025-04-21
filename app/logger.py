import sys
from loguru import logger

def setup_logger():
    logger.remove()
    
    logger.add(
        "logs/api.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[source]} {message}"
    )
    
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>"
    )