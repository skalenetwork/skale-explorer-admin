import logging
import os

from admin import EXPLORERS_META_DATA_PATH, ENVS_DIR_PATH
from admin.utils.helper import read_json, write_json, read_env_file

logger = logging.getLogger(__name__)


def get_schain_endpoint(schain_name):
    return get_schain_meta(schain_name)['ENDPOINT']


def get_explorer_endpoint(schain_name):
    explorer_port = get_schain_meta(schain_name)['PROXY_PORT']
    return f'http://127.0.0.1:{explorer_port}'


def get_schain_meta(schain_name):
    env_file_path = os.path.join(ENVS_DIR_PATH, f'{schain_name}.env')
    return read_env_file(env_file_path)


def get_explorers_meta():
    return read_json(EXPLORERS_META_DATA_PATH)['explorers']
