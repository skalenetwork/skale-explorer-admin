## Delete Last Transactions Script

This script allows you to delete the oldest transactions from a database, retaining only the most recent transactions based on the number you specify.

### Usage

```bash
./scripts/delete_last_transactions.sh [-y | --yes] <schain_name> <N>
```

- `<schain_name>`: The name of the blockchain (schain) for which the transactions will be deleted.
- `<N>`: The number of newest transactions that you want to keep in the database.

### Options

- `-y`, `--yes`: (Optional) Skip the confirmation prompt and proceed directly with the deletion.

### How It Works

1. **Confirmation Prompt**: By default, after running the script, you'll be prompted to confirm the deletion by typing `"yes"`. If you use the `-y` or `--yes` flag, the script skips this prompt.

2. **Transaction Deletion**: The script will delete `(total_number_of_transactions - N)` transactions from the `transactions` table, where `total_number_of_transactions` is the current total number of transactions in the database.

3. **Error Handling**: The script checks if:
   - The specified container is running.
   - The value of `N` is not greater than the total number of transactions.

   If any of these checks fail, the script will exit with an error message.

### Example

To delete the oldest transactions from the `my_schain` blockchain, keeping the last 100 transactions:

```bash
./scripts/delete_last_transactions.sh my_schain 100
```

To run the same command without needing to confirm:

```bash
./scripts/delete_last_transactions.sh --yes my_schain 100
```
