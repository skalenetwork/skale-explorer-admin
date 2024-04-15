import logging
import os
import subprocess

from admin import (DOCKER_COMPOSE_CONFIG_PATH, DOCKER_COMPOSE_BIN_PATH,
                   COMPOSE_HTTP_TIMEOUT, BLOCKSCOUT_DATA_DIR, HOST_DIR_PATH, HOST_ENV_DIR_PATH)
from admin.configs.meta import (update_meta_data, get_schain_meta, get_explorers_meta,
                                set_schain_upgraded, is_schain_upgraded, verified_contracts)
from admin.configs.nginx import regenerate_nginx_config
from admin.configs.schains import generate_config
from admin.core.containers import (get_free_port, restart_nginx,
                                   is_explorer_running, remove_explorer)
from admin.core.endpoints import is_dkg_passed, get_schain_endpoint, get_first_block, get_chain_id
from admin.core.verify import verify
from admin.migrations.revert_reasons import upgrade
from admin.utils.helper import find_sequential_free_ports, write_json_into_env

logger = logging.getLogger(__name__)


def run_explorer(schain_name):
    env_file_path = os.path.join(HOST_ENV_DIR_PATH, f'{schain_name}.env')
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
    ports_env = {
        'PROXY_PORT': str(base_port),
        'DB_PORT': str(base_port + 1),
        'STATS_PORT': str(base_port + 2),
        'STATS_DB_PORT': str(base_port + 3),
    }
    schain_env = {
        'SCHAIN_NAME': schain_name,
        'SCHAIN_APP_NAME': schain_name,
        'CHAIN_ID': str(get_chain_id(schain_name)),
        'ENDPOINT': get_schain_endpoint(schain_name),
        'WS_ENDPOINT': get_schain_endpoint(schain_name, ws=True),
        'SCHAIN_DATA_DIR': blockscout_data_dir,
        'CONFIG_PATH': config_host_path,
    }
    return {
        'COMPOSE_PROJECT_NAME': schain_name,
        **ports_env,
        **schain_env
    }


def run_explorer_for_schain(schain_name):
    schain_meta = get_schain_meta(schain_name)
    if schain_meta and schain_meta.get('sync') is True:
        endpoint = schain_meta['endpoint']
        ws_endpoint = schain_meta['ws_endpoint']
    else:
        endpoint = get_schain_endpoint(schain_name)
        ws_endpoint = get_schain_endpoint(schain_name, ws=True)
    chain_id = get_chain_id(schain_name)
    if endpoint and ws_endpoint:
        run_explorer(schain_name)
    else:
        logger.warning(f"Couldn't create blockexplorer instance for {schain_name}")


def check_explorer_for_schain(schain_name):
    explorers = get_explorers_meta()
    if schain_name not in explorers and not is_dkg_passed(schain_name):
        return
    if schain_name not in explorers:
        run_explorer_for_schain(schain_name)
        set_schain_upgraded(schain_name)
    if not is_explorer_running(schain_name):
        if not is_explorer_running(schain_name):
            logger.warning(f'Blockscout is not working for {schain_name}. Recreating...')
        else:
            logger.warning(f'Blockscout version is outdated for {schain_name}. Recreating...')
        remove_explorer(schain_name)
        if not is_schain_upgraded(schain_name):
            upgrade(schain_name)
        run_explorer_for_schain(schain_name)
    if not verified_contracts(schain_name) and is_explorer_running(schain_name):
        verify(schain_name)
