import logging
import os
import subprocess
from time import sleep

import requests

from admin import (DOCKER_COMPOSE_CONFIG_PATH, DOCKER_COMPOSE_BIN_PATH,
                   BLOCKSCOUT_DATA_DIR, ENVS_DIR_PATH, BLOCKSCOUT_PROXY_CONFIG_DIR,
                   BLOCKSCOUT_ASSETS_DIR, SSL_ENABLED,
                   HOST_DOMAIN, BLOCKSCOUT_PROXY_SSL_CONFIG_DIR, HOST_SSL_DIR_PATH,
                   WALLET_CONNECT_PROJECT_ID, BLOCKSCOUT_TAG, IS_TESTNET)
from admin.configs.meta import get_explorer_endpoint
from admin.configs.nginx import regenerate_nginx_config
from admin.configs.schains import generate_config
from admin.core.containers import (restart_nginx,
                                   is_explorer_running)
from admin.core.endpoints import is_dkg_passed, get_schain_endpoint, get_chain_id
from admin.core.verify import verify
from admin.utils.helper import find_sequential_free_ports, write_json_into_env

logger = logging.getLogger(__name__)


def run_explorer_for_schain(schain_name, update=False):
    env_file_path = os.path.join(ENVS_DIR_PATH, f'{schain_name}.env')
    if not os.path.exists(env_file_path) or update:
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
        '-d'
    ]
    subprocess.run(command, env={**os.environ})
    regenerate_nginx_config()
    restart_nginx()
    internal_endpoint = get_explorer_endpoint(schain_name)
    logger.info(f'{schain_name} explorer is running on {internal_endpoint} endpoint internally')
    logger.info(f'{schain_name} explorer is running on {schain_name}. subdomain')


def stop_explorer_for_schain(schain_name):
    env_file_path = os.path.join(ENVS_DIR_PATH, f'{schain_name}.env')
    command = [
        DOCKER_COMPOSE_BIN_PATH,
        'compose',
        '-f',
        DOCKER_COMPOSE_CONFIG_PATH,
        '--env-file',
        env_file_path,
        'down',
    ]
    subprocess.run(command, env={**os.environ})
    logger.info('sChain explorer is stopped')


def generate_blockscout_env(schain_name):
    base_port = find_sequential_free_ports(5)
    config_host_path = generate_config(schain_name)
    blockscout_data_dir = f'{BLOCKSCOUT_DATA_DIR}/{schain_name}'
    network = 'testnet' if IS_TESTNET else 'mainnet'
    chains_metadata_url = \
        f'https://raw.githubusercontent.com/skalenetwork/skale-network/master/metadata/{network}/chains.json' # noqa
    schain_app_name = requests.get(chains_metadata_url).json()[schain_name]['alias']
    ports_env = {
        'PROXY_PORT': str(base_port),
        'DB_PORT': str(base_port + 1),
        'STATS_PORT': str(base_port + 2),
        'STATS_DB_PORT': str(base_port + 3),
    }
    schain_env = {
        'SCHAIN_NAME': schain_name,
        'SCHAIN_APP_NAME': schain_app_name,
        'CHAIN_ID': str(get_chain_id(schain_name)),
        'ENDPOINT': get_schain_endpoint(schain_name),
        'WS_ENDPOINT': get_schain_endpoint(schain_name, ws=True),
        'NEXT_PUBLIC_IS_TESTNET': IS_TESTNET
    }
    if WALLET_CONNECT_PROJECT_ID:
        schain_env.update({
            'NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID': WALLET_CONNECT_PROJECT_ID
        })
    volumes_env = {
        'SCHAIN_DATA_DIR': blockscout_data_dir,
        'BLOCKSCOUT_ASSETS_DIR': BLOCKSCOUT_ASSETS_DIR,
        'CONFIG_PATH': config_host_path,
    }
    if SSL_ENABLED:
        network_env = {
            'HOST': HOST_DOMAIN,
            'PROXY_BASE_PORT': 443,
            'NEXT_PUBLIC_API_WEBSOCKET_PROTOCOL': 'wss',
            'NEXT_PUBLIC_API_PROTOCOL': 'https',
            'STATS_PROTOCOL': 'https',
            'NEXT_PUBLIC_APP_PROTOCOL': 'https',
            'BLOCKSCOUT_PROXY_CERTS_PATH': HOST_SSL_DIR_PATH,
            'BLOCKSCOUT_PROXY_CONFIG_DIR': BLOCKSCOUT_PROXY_SSL_CONFIG_DIR,
        }
    else:
        public_ip = requests.get('https://api.ipify.org').content.decode('utf8')
        network_env = {
            'HOST': str(public_ip),
            'BLOCKSCOUT_PROXY_CONFIG_DIR': BLOCKSCOUT_PROXY_CONFIG_DIR,
        }
    return {
        'COMPOSE_PROJECT_NAME': schain_name,
        'DOCKER_TAG': BLOCKSCOUT_TAG,
        **ports_env,
        **schain_env,
        **volumes_env,
        **network_env
    }


def check_explorer_for_schain(schain_name, update=False):
    if not is_dkg_passed(schain_name):
        return
    if not is_explorer_running(schain_name):
        run_explorer_for_schain(schain_name, update)
        sleep(60)
        verify(schain_name)
