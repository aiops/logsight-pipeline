import logging.config
import os
import platform
import sys
from multiprocessing import set_start_method

# hello world
from logsight_pipeline.configs.globals import path
from logsight_pipeline.configs.configuration import PipelineConfig
from logsight.logger.configuration import LogConfig
from builders.pipeline_builder import PipelineBuilder
from logsight.services.service_provider import ServiceProvider

logging.config.dictConfig(LogConfig().config)
logger = logging.getLogger('logsight')
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
