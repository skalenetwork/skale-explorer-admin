import argparse
import logging
import os
from functools import wraps
from threading import Thread
from time import sleep

from admin import ABI_FILEPATH
from admin.core.endpoints import get_all_names
from admin.core.explorers import check_explorer_for_schain
from admin.core.verify import verify
from admin.utils.logger import init_logger

logger = logging.getLogger(__name__)


def daemon(delay=60):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f'Initiating {func.__name__}')
            while True:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.exception(f'{func.__name__} failed with: {e}')
                    logger.warning(f'Restarting {func.__name__}...')
                sleep(delay)
        return wrapper
    return actual_decorator


@daemon()
def check_explorer_status():
    schains = get_all_names()
    for schain_name in schains:
        check_explorer_for_schain(schain_name)


def verify_contracts():
    schains = get_all_names()
    for schain_name in schains:
        verify(schain_name)


def main():
    assert os.path.isfile(ABI_FILEPATH), "ABI not found"

    parser = argparse.ArgumentParser(description='Process some options.')

    # Define optional arguments
    parser.add_argument('--verify', action='store_true', help='Run the verification process')
    parser.add_argument('--update', action='store_true', help='Run the update process')

    # Parse arguments
    args = parser.parse_args()
    if args.verify:
        logger.info("Verification process is running...")
        verify_contracts()
    else:
        logger.info("Status check process is running...")
        check_explorer_status()


if __name__ == '__main__':
    init_logger()
    main()
