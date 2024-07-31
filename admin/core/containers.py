import logging
import os
import subprocess

import docker

from admin import DOCKER_COMPOSE_BIN_PATH, DOCKER_COMPOSE_CONFIG_PATH
from admin.utils.logger import init_logger

init_logger()
logger = logging.getLogger(__name__)
dutils = docker.DockerClient()


CONTAINER_NOT_FOUND = 'not_found'
RUNNING_STATUS = 'running'


def is_explorer_running(schain_name):
    container_name = f'{schain_name}_proxy'
    return get_info(container_name) == 'running'


def get_info(container_id: str):
    try:
        container = dutils.containers.get(container_id)
        return container.status
    except docker.errors.NotFound:
        logger.warning(
            f'Can not get info - no such container: {container_id}')
        return CONTAINER_NOT_FOUND


def restart_nginx():
    nginx = dutils.containers.get('nginx')
    logger.info('Restarting nginx container...')
    nginx.exec_run('nginx -s reload')


def run_blockscout_containers(env_file_path):
    command = [
        DOCKER_COMPOSE_BIN_PATH,
        'compose',
        '-f',
        DOCKER_COMPOSE_CONFIG_PATH,
        '--env-file',
        env_file_path,
        'up',
        '-d'
    ]
    subprocess.run(command, env={**os.environ})


def stop_blockscout_containers(env_file_path):
    command = [
        DOCKER_COMPOSE_BIN_PATH,
        'compose',
        '-f',
        DOCKER_COMPOSE_CONFIG_PATH,
        '--env-file',
        env_file_path,
        'down'
    ]
    subprocess.run(command, env={**os.environ})


def restart_blockscout_containers(env_file_path):
    command = [
        DOCKER_COMPOSE_BIN_PATH,
        'compose',
        '-f',
        DOCKER_COMPOSE_CONFIG_PATH,
        '--env-file',
        env_file_path,
        'restart'
    ]
    subprocess.run(command, env={**os.environ})

