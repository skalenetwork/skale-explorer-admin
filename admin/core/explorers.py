import logging
import os
import subprocess
from time import sleep

import requests

from admin import (DOCKER_COMPOSE_CONFIG_PATH, DOCKER_COMPOSE_BIN_PATH,
                   BLOCKSCOUT_DATA_DIR, ENVS_DIR_PATH, BLOCKSCOUT_PROXY_CONFIG_DIR, BLOCKSCOUT_ASSETS_DIR)
from admin.configs.nginx import regenerate_nginx_config
from admin.configs.schains import generate_config
from admin.core.containers import (restart_nginx,
                                   is_explorer_running)
from admin.core.endpoints import is_dkg_passed, get_schain_endpoint, get_chain_id
from admin.core.verify import verify
from admin.utils.helper import find_sequential_free_ports, write_json_into_env

logger = logging.getLogger(__name__)


def run_explorer_for_schain(schain_name):
    env_file_path = os.path.join(ENVS_DIR_PATH, f'{schain_name}.env')
    if not os.path.exists(env_file_path):
        env_data = generate_blockscout_env(schain_name)
        write_json_into_env(env_file_path, env_data)
        logger.info(f'Env for {schain_name} is generated: {env_file_path}')
    command = [
        DOCKER_COMPOSE_BIN_PATH,
        'compose',
        '-f',
        DOCKER_COMPOSE_CONFIG_PATH,
        '--env-file',
        env_file_path,
        'up',
        '-d',
        '--build'
    ]
    subprocess.run(command, env={**os.environ})
    regenerate_nginx_config()
    restart_nginx()
    logger.info(f'sChain explorer is running on {schain_name}. subdomain')


def generate_blockscout_env(schain_name):
    base_port = find_sequential_free_ports(5)
    config_host_path = generate_config(schain_name)
    blockscout_data_dir = f'{BLOCKSCOUT_DATA_DIR}/{schain_name}'
    public_ip = requests.get('https://api.ipify.org').content.decode('utf8')
    network_env = {
        'PROXY_PORT': str(base_port),
        'DB_PORT': str(base_port + 1),
        'STATS_PORT': str(base_port + 2),
        'STATS_DB_PORT': str(base_port + 3),
        'HOST': str(public_ip),
    }
    schain_env = {
        'SCHAIN_NAME': schain_name,
        'SCHAIN_APP_NAME': schain_name,
        'CHAIN_ID': str(get_chain_id(schain_name)),
        'ENDPOINT': get_schain_endpoint(schain_name),
        'WS_ENDPOINT': get_schain_endpoint(schain_name, ws=True),
    }
    volumes_env = {
        'SCHAIN_DATA_DIR': blockscout_data_dir,
        'BLOCKSCOUT_PROXY_CONFIG_DIR': BLOCKSCOUT_PROXY_CONFIG_DIR,
        'BLOCKSCOUT_ASSETS_DIR': BLOCKSCOUT_ASSETS_DIR,
        'CONFIG_PATH': config_host_path,
    }
    return {
        'COMPOSE_PROJECT_NAME': schain_name,
        **network_env,
        **schain_env,
        **volumes_env
    }


def check_explorer_for_schain(schain_name):
    if not is_dkg_passed(schain_name):
        return
    if not is_explorer_running(schain_name):
        run_explorer_for_schain(schain_name)
        sleep(60)
        verify(schain_name)
