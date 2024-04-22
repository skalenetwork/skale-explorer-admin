import argparse
import logging
import os

from admin import ABI_FILEPATH
from admin.core.endpoints import get_all_names
from admin.core.explorers import check_explorer_for_schain, run_explorer_for_schain
from admin.core.verify import verify
from admin.utils.logger import init_logger

logger = logging.getLogger(__name__)


def run_explorers():
    schains = get_all_names()
    for schain_name in schains:
        check_explorer_for_schain(schain_name)


def verify_contracts():
    schains = get_all_names()
    for schain_name in schains:
        verify(schain_name)


def update_explorers():
    schains = get_all_names()
    for schain_name in schains:
        run_explorer_for_schain(schain_name, update=True)


def stop_explorers():
    schains = get_all_names()
    for schain_name in schains:
        stop_explorer_for_schain(schain_name)


def main():
    assert os.path.isfile(ABI_FILEPATH), "ABI not found"

    parser = argparse.ArgumentParser(description='Process some options.')

    parser.add_argument('--verify', action='store_true', help='Run the verification process')
    parser.add_argument('--update', action='store_true', help='Run the update process')
    parser.add_argument('--down', action='store_true', help='Stop explorers')

    args = parser.parse_args()
    if args.verify:
        logger.info("Verification process is running...")
        verify_contracts()
    elif args.update:
        logger.info("Update process is running...")
        update_explorers()
    elif args.down:
        logger.info("Stopping explorers...")
        update_explorers()
    else:
        logger.info("Run explorers process is running...")
        run_explorers()


if __name__ == '__main__':
    init_logger()
    main()
