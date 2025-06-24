from pymongo import MongoClient
from datetime import datetime

# Your MongoDB connection string
MONGODB_URL = "mongodb+srv://fakeslakke:B8PYEtEguzChJCsr@cluster0.ghuc7qq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to the sample_analytics database
client = MongoClient(MONGODB_URL)
db = client["sample_analytics"]

# Convert dates to timestamps (milliseconds since epoch) for 2015
start_2015 = int(datetime(2015, 1, 1).timestamp() * 1000)
mid_2015 = int(datetime(2015, 7, 1).timestamp() * 1000)
end_2015 = int(datetime(2016, 1, 1).timestamp() * 1000)

print("Date ranges:")
print(f"Start 2015: {start_2015}")
print(f"Mid 2015: {mid_2015}")
print(f"End 2015: {end_2015}")

# First, let's find Dr. Angela Brown's account IDs
customers = db["customers"]
katherine = customers.find_one({"name": "Dr. Angela Brown"})

if not katherine:
    print("Dr. Angela Brown not found in customers collection")
    # Let's see what names are available
    print("Available customer names:")
    for customer in customers.find({}, {"name": 1}).limit(10):
        print(f"  - {customer['name']}")
    exit()

print(f"Found Dr. Angela Brown with account IDs: {katherine['accounts']}")

# Now find her transactions
transactions = db["transactions"]
katherine_accounts = katherine["accounts"]

# Find all transaction documents for Katherine's accounts
transaction_docs = list(transactions.find({"account_id": {"$in": katherine_accounts}}))

if not transaction_docs:
    print("No transaction documents found for Dr. Angela Brown's accounts")
    exit()

print(f"Found {len(transaction_docs)} transaction documents for Dr. Angela Brown")

# Process transactions for 2015
first_half_transactions = []
second_half_transactions = []
first_half_total = 0
second_half_total = 0

for doc in transaction_docs:
    print(
        f"\nProcessing account {doc['account_id']} with {doc['transaction_count']} transactions"
    )

    for transaction in doc["transactions"]:
        # Handle different date formats
        if isinstance(transaction["date"], dict) and "$date" in transaction["date"]:
            transaction_date = transaction["date"]["$date"]
        else:
            # Date is already a datetime object
            transaction_date = int(transaction["date"].timestamp() * 1000)

        # Check if transaction is in 2015
        if start_2015 <= transaction_date < end_2015:
            transaction_info = {
                "account_id": doc["account_id"],
                "date": transaction["date"]
                if isinstance(transaction["date"], datetime)
                else datetime.fromtimestamp(transaction_date / 1000),
                "amount": transaction["amount"],
                "transaction_code": transaction["transaction_code"],
                "symbol": transaction["symbol"],
                "price": float(transaction["price"]),
                "total": float(transaction["total"]),
            }

            # Split into first half (Jan-June) and second half (July-Dec)
            if transaction_date < mid_2015:
                first_half_transactions.append(transaction_info)
                first_half_total += transaction["amount"]
            else:
                second_half_transactions.append(transaction_info)
                second_half_total += transaction["amount"]

# Display results
print(f"\n{'=' * 60}")
print(f"Dr. Angela Brown'S 2015 TRANSACTION ANALYSIS")
print(f"{'=' * 60}")

print(f"\nFIRST HALF 2015 (January - June):")
print(f"Total transactions: {len(first_half_transactions)}")
print(f"Total amount: {first_half_total}")
if first_half_transactions:
    print("Transaction details:")
    for i, txn in enumerate(first_half_transactions, 1):
        print(
            f"  {i}. {txn['date'].strftime('%Y-%m-%d')} | {txn['transaction_code'].upper()} | "
            f"{txn['symbol'].upper()} | Amount: {txn['amount']} | "
            f"Price: ${txn['price']:.2f} | Total: ${txn['total']:.2f}"
        )

print(f"\nSECOND HALF 2015 (July - December):")
print(f"Total transactions: {len(second_half_transactions)}")
print(f"Total amount: {second_half_total}")
if second_half_transactions:
    print("Transaction details:")
    for i, txn in enumerate(second_half_transactions, 1):
        print(
            f"  {i}. {txn['date'].strftime('%Y-%m-%d')} | {txn['transaction_code'].upper()} | "
            f"{txn['symbol'].upper()} | Amount: {txn['amount']} | "
            f"Price: ${txn['price']:.2f} | Total: ${txn['total']:.2f}"
        )

print(f"\nSUMMARY:")
print(f"First half total amount: {first_half_total}")
print(f"Second half total amount: {second_half_total}")
print(f"Total 2015 amount: {first_half_total + second_half_total}")

# Close the connection
client.close()
