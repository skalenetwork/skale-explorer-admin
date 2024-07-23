#!/bin/bash

schain="$1"
threads="$2"
shift 2

for table in "$@"; do
    echo "Dumping $table..."
    ./threading.sh "$schain" "$threads" "$table" > /dev/null 2>&1
done
