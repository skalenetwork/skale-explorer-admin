import json
import logging
import socket

from admin import ZERO_ADDRESS

logger = logging.getLogger(__name__)


def get_schain_originator(schain: dict):
    if schain['originator'] == ZERO_ADDRESS:
        return schain['mainnetOwner']
    return schain['originator']


def read_json(path, mode='r'):
    with open(path, mode=mode, encoding='utf-8') as data_file:
        return json.load(data_file)


def write_json(path, content):
    with open(path, 'w') as outfile:
        json.dump(content, outfile, indent=4)


def read_env_file(path):
    combined_env = {}
    with open(path, 'r') as file:
        for line in file:
            # Strip whitespace and skip empty lines or lines that start with '#'
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                combined_env[key] = value
    return combined_env


def write_json_into_env(path, data):
    with open(path, 'w') as file:
        for key, value in data.items():
            file.write(f"{key}={value}\n")


def find_sequential_free_ports(count=5):
    """
    Finds a range of sequential free ports by attempting to bind sockets on contiguous ports.

    :param count: Number of sequential ports to find.
    :return: A list of `count` sequential free ports if found, otherwise None.
    """
    sockets = []
    base_port = 1024
    last_port = 50000

    while base_port < last_port - count + 1:
        success = True
        for offset in range(count):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('', base_port + offset))
                sockets.append(s)
            except socket.error:
                success = False
                for s in sockets:
                    s.close()
                sockets = []
                base_port += offset + 1
                break

        if success:
            return base_port
    return None
