import logging
import os

from admin import EXPLORERS_META_DATA_PATH, ENVS_DIR_PATH, SSL_ENABLED
from admin.utils.helper import read_json, read_env_file

logger = logging.getLogger(__name__)


def get_schain_endpoint(schain_name):
    return get_schain_meta(schain_name)['ENDPOINT']


def get_explorer_endpoint(schain_name):
    schain_env = get_schain_meta(schain_name)
    if SSL_ENABLED:
        proxy_endpoint = f'https://{schain_env["HOST"]}:{schain_env["PROXY_PORT"]}'
    else:
        proxy_endpoint = f'http://{schain_env["HOST"]}:{schain_env["PROXY_PORT"]}'
    return proxy_endpoint


def get_schain_meta(schain_name):
    env_file_path = os.path.join(ENVS_DIR_PATH, f'{schain_name}.env')
    return read_env_file(env_file_path)


def get_explorers_meta():
    return read_json(EXPLORERS_META_DATA_PATH)['explorers']
