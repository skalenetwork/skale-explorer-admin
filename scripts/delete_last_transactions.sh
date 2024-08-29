#!/bin/bash

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <schain_name> <N>"
    exit 1
fi

CONTAINER_NAME="$1_db"
N=$2

if ! docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Error: No running container found with the name '$CONTAINER_NAME'."
    exit 1
fi

TOTAL_TRANSACTIONS=$(docker exec "$CONTAINER_NAME" psql -U blockscout -d blockscout -t -c "SELECT COUNT(*) FROM transactions;" | xargs)

if [ "$N" -gt "$TOTAL_TRANSACTIONS" ]; then
    echo "Error: N ($N) is greater than the total number of transactions ($TOTAL_TRANSACTIONS)."
    exit 1
fi

echo "Total number of transactions: $TOTAL_TRANSACTIONS"
echo "You are about to delete the last $(($TOTAL_TRANSACTIONS - $N)) transactions from the 'transactions' table."
read -p "Are you sure you want to proceed? Type 'yes' to continue: " CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo "Operation aborted. No transactions were deleted."
    exit 0
fi

docker exec "$CONTAINER_NAME" psql -U blockscout -d blockscout -c "
WITH rows_to_delete AS (
    SELECT ctid
    FROM transactions
    ORDER BY block_timestamp ASC
    LIMIT (SELECT COUNT(*) FROM transactions) - $N
)
DELETE FROM transactions
WHERE ctid IN (SELECT ctid FROM rows_to_delete);
"

if [ $? -eq 0 ]; then
    echo "Successfully deleted the last $(($TOTAL_TRANSACTIONS - $N)) transactions from the 'transactions' table."
else
    echo "Failed to delete transactions. Please check your input parameters and try again."
    exit 1
fi
