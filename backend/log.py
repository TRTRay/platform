from loguru import logger
import logging

# Access Log
alog = logger.bind(module="access_log")

# Mosquitto Log
mlog = logger.bind(module="mosquitto")

# Genearl Log
log = logger.bind(module="application")

alog.add(
    "./runtime/api_access.log",
    format="{message}",
    level="TRACE",
    filter=lambda record: record["extra"].get("module") == "access_log",
)

mlog.add(
    "./runtime/mosquitto.log",
    format="{time} {level} {message}",
    level="TRACE",
    filter=lambda record: record["extra"].get("module") == "mosquitto",
)


log.add(
    "./runtime/application.log",
    format="{time} {level} {message}",
    level="TRACE",
    filter=lambda record: record["extra"].get("module") == "application",
)

logger.add("./runtime/verbose.log", format="{time} {level} {message}", level="TRACE")
logger.info("Log Init Done")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        alog.log(level, record.getMessage())

    def write(self, message):
        if message.rstrip() != "":
            alog.info(message.rstrip())
