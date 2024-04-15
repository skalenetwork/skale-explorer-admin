import logging
import os

from admin import EXPLORERS_META_DATA_PATH, ENVS_DIR_PATH
from admin.utils.helper import read_json, write_json, read_env_file

logger = logging.getLogger(__name__)


def create_meta_file():
    empty_data = {
        'explorers': {}
    }
    write_json(EXPLORERS_META_DATA_PATH, empty_data)


def verified_contracts(schain_name):
    return get_schain_meta(schain_name).get('contracts_verified') is True


def set_schain_upgraded(schain_name):
    meta = read_json(EXPLORERS_META_DATA_PATH)
    schain_meta = meta['explorers'][schain_name]
    schain_meta['updated'] = True
    write_json(EXPLORERS_META_DATA_PATH, meta)


def update_meta_data(schain_name, proxy_port, db_port, stats_port,
                     stats_db_port, scv_port, endpoint, ws_endpoint, first_block):
    logger.info(f'Updating meta data for {schain_name}')
    meta_data = read_json(EXPLORERS_META_DATA_PATH)
    explorers = meta_data['explorers']
    schain_meta = explorers.get(schain_name, {})
    schain_meta.update({
        'proxy_port': proxy_port,
        'db_port': db_port,
        'stats_port': stats_port,
        'stats_db_port': stats_db_port,
        'scv_port': scv_port,
        'endpoint': endpoint,
        'ws_endpoint': ws_endpoint,
        'first_block': first_block
    })
    explorers.update({
        schain_name: schain_meta
    })
    write_json(EXPLORERS_META_DATA_PATH, meta_data)


def get_schain_endpoint(schain_name):
    return get_schain_meta(schain_name)['ENDPOINT']


def get_explorer_endpoint(schain_name):
    explorer_port = get_schain_meta(schain_name)['PROXY_PORT']
    return f'http://127.0.0.1:{explorer_port}'


def get_schain_meta(schain_name):
    env_file_path = os.path.join(ENVS_DIR_PATH, f'{schain_name}.env')
    return read_env_file(env_file_path)


def set_chain_verified(schain_name):
    data = read_json(EXPLORERS_META_DATA_PATH)
    data['explorers'][schain_name]['contracts_verified'] = True
    write_json(EXPLORERS_META_DATA_PATH, data)


def get_explorers_meta():
    return read_json(EXPLORERS_META_DATA_PATH)['explorers']
