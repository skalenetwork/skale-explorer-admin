#!/usr/bin/env bash

set -e

WORKDIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
HOST_DIR_PATH=$WORKDIR docker-compose -f $WORKDIR/docker-compose.yaml up -d --build