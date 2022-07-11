import logging
from os.path import join
from time import sleep

import requests
import json

from web3 import Web3

from admin import SCHAIN_CONFIG_DIR_PATH, EXPLORERS_META_DATA_PATH
from endpoints import read_json, write_json

logger = logging.getLogger(__name__)


def verify(schain_name):
    logger.info(f'Verifying contracts for {schain_name}')
    config = read_json(join(SCHAIN_CONFIG_DIR_PATH, f'{schain_name}.json'))
    j = config['verify']
    for verifying_address in j.keys():
        if not config['verification_status'][verifying_address]:
            logging.info(f'Verifying {verifying_address} contract')
            contract_meta = j[verifying_address]
            contract = {
                'contractaddress': verifying_address,
                'contractname': contract_meta['name'],
                'compilerversion': f'v{contract_meta["solcLongVersion"]}',
                'sourceCode': json.dumps(contract_meta['input'])
            }
            response = send_verify_request(schain_name, contract)
            if response and check_verify_status(schain_name, response['result']):
                set_contract_verified(schain_name, verifying_address)
    all_verified = True
    upd_config = read_json(join(SCHAIN_CONFIG_DIR_PATH, f'{schain_name}.json'))
    for verifying_address in j.keys():
        if not upd_config['verification_status'][verifying_address]:
            logger.info(f'Contract {verifying_address} is not verified')
            all_verified = False
    if all_verified:
        logger.info(f'All contracts are verified for {schain_name}')
        data = read_json(EXPLORERS_META_DATA_PATH)
        data[schain_name]['contracts_ verified'] = True
        write_json(EXPLORERS_META_DATA_PATH, data)


def get_verified_contract_list(schain_name):
    data = read_json(EXPLORERS_META_DATA_PATH)
    schain_explorer_endpoint = f'http://127.0.0.1:{data[schain_name]["port"]}'
    headers = {'content-type': 'application/json'}
    addresses = []
    try:
        result = requests.get(
            f'{schain_explorer_endpoint}/api?module=contract&action=listcontracts&filter=verified',
            headers=headers
        ).json()['result']
        addresses = [Web3.toChecksumAddress(contract['Address']) for contract in result]
    except requests.exceptions.ConnectionError as e:
        logger.warning(f'get_contract_list failed with {e}')
    return addresses


def get_veify_url(schain_name):
    data = read_json(EXPLORERS_META_DATA_PATH)
    schain_explorer_endpoint = f'http://127.0.0.1:{data[schain_name]["port"]}'
    return f'{schain_explorer_endpoint}/api?module=contract&action=verifysourcecode&codeformat=solidity-standard-json-input'


def send_verify_request(schain_name, verification_data):
    headers = {'content-type': 'application/json'}
    try:
        return requests.post(
            get_veify_url(schain_name),
            data=json.dumps(verification_data),
            headers=headers
        ).json()
    except requests.exceptions.ConnectionError as e:
        logger.warning(f'verifying_address failer with {e}')


def is_contract_verified(schain_name, address):
    data = read_json(EXPLORERS_META_DATA_PATH)
    schain_explorer_endpoint = f'http://127.0.0.1:{data[schain_name]["port"]}'
    headers = {'content-type': 'application/json'}
    try:
        result = requests.get(
            f'{schain_explorer_endpoint}/api?module=contract&action=getabi&address={address}',
            headers=headers
        ).json()['status']
        return False if int(result) == 0 else True
    except requests.exceptions.ConnectionError as e:
        logger.warning(f'is_contract_verified failed with {e}')


def check_verify_status(schain_name, uid):
    if uid == 'Smart-contract already verified':
        logger.info('Contract already verified')
        return True
    data = read_json(EXPLORERS_META_DATA_PATH)
    schain_explorer_endpoint = f'http://127.0.0.1:{data[schain_name]["port"]}'
    headers = {'content-type': 'application/json'}
    try:
        while True:
            url = f'{schain_explorer_endpoint}/api?module=contract&action=checkverifystatus&guid={uid}'
            response = requests.get(
                url,
                headers=headers
            ).json()
            if response['result'] == 'Pending in queue' or response['result'] == 'Unknown UID':
                logger.info(f'Verify status: {response["result"]}...')
                sleep(10)
            else:
                if response['result'] == 'Pass - Verified':
                    logger.info('Contract successfully verified')
                    return True
                elif response['result'] == 'Fail - Unable to verify':
                    logger.info('Failed to verified contract')
                else:
                    logger.info(response['result'])
                break
    except requests.exceptions.ConnectionError as e:
        logger.warning(f'checkverifystatus failed with {e}')
    return False
