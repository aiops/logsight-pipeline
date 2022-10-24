import logging.config
import os
import platform
import sys
from multiprocessing import set_start_method

from logsight_sdk.authentication import LogsightAuthentication
from logsight_sdk.config import get_tags_from_env, set_host
from logsight_sdk.logger import LogsightLogger

# hello world
from logsight_pipeline.configs.globals import path
from logsight_pipeline.configs.configuration import PipelineConfig
from logsight.logger.configuration import LogConfig
from builders.pipeline_builder import PipelineBuilder
from logsight.services.service_provider import ServiceProvider

logging.config.dictConfig(LogConfig().config)
EMAIL = os.getenv('LOGSIGHT_USER')
PASSWORD = os.getenv('LOGSIGHT_PASSWORD')
env_tags = get_tags_from_env()  # {"service": "redis"}
set_host("https://logsight.ai/api/v1/")
auth = LogsightAuthentication(email=EMAIL, password=PASSWORD)

handler = LogsightLogger(auth.token)
handler.setLevel(logging.DEBUG)
handler.set_tags(tags=env_tags)


logger = logging.getLogger('logsight')
logger.addHandler(handler)
logger.debug(f"Using config path {path}")


# needed for running on Windows or macOS
if platform.system() != 'Linux':
    logger.debug(f"Start method fork for system {platform.system()}.")
    set_start_method("fork", force=True)


def verify_services():
    # Verify elasticsearch connection
    es = ServiceProvider.provide_elasticsearch()
    es.connect()
    logger.info("Elasticsearch service available.")

    # Verify db connection
    db = ServiceProvider.provide_postgres()
    db.connect()
    logger.info("Postgres database service available.")


def run_pipeline():
    pipeline_cfg = PipelineConfig().pipeline
    builder = PipelineBuilder()
    pipeline = builder.build(pipeline_cfg)
    pipeline.run()


def run():
    verify_services()
    run_pipeline()

if __name__ == '__main__':
    run()
