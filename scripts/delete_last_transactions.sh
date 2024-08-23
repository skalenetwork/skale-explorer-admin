#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <container_name> <N>"
    exit 1
fi

CONTAINER_NAME=$1
N=$2

TOTAL_TRANSACTIONS=$(docker exec "$CONTAINER_NAME" psql -U blockscout -d blockscout -t -c "SELECT COUNT(*) FROM transactions;" | xargs)

if [ "$N" -gt "$TOTAL_TRANSACTIONS" ]; then
    echo "Error: N ($N) is greater than the total number of transactions ($TOTAL_TRANSACTIONS)."
    exit 1
fi

echo "You are about to delete the last $N transactions from the 'transactions' table."
echo "Total number of transactions: $TOTAL_TRANSACTIONS"
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
    LIMIT $N
)
DELETE FROM transactions
WHERE ctid IN (SELECT ctid FROM rows_to_delete);
"

if [ $? -eq 0 ]; then
    echo "Successfully deleted the last $N transactions from the 'transactions' table."
else
    echo "Failed to delete transactions. Please check your input parameters and try again."
    exit 1
fi
