from pymongo import MongoClient
import os  # Import os to access environment variables if MONGODB_URL is set that way

# The aggregation pipeline
pipeline = [
    {"$match": {"account_id": 794875}},
    {"$unwind": "$transactions"},
    {"$match": {"transactions.transaction_code": "sell"}},
    {
        "$group": {
            "_id": None,
            "total_sell_transactions": {"$sum": 1},
        }
    },
    {"$project": {"_id": 0, "total_sell_transactions": 1}},
]

# --- MongoDB Connection Details ---
# Ideally, put your MONGODB_URI in environment variable for security
# If not, fallback to hardcoded (for testing only)

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://fakeslakke:B8PYEtEguzChJCsr@cluster0.ghuc7qq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)
DB_NAME = "sample_analytics"
COLLECTION_NAME = "transactions"

client = None

try:
    # 1. Establish connection to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print(f"Using database: '{DB_NAME}', collection: '{COLLECTION_NAME}'")

    # 2. Execute the aggregation pipeline
    results_cursor = collection.aggregate(pipeline)

    # 3. Process and print the results
    found_results = False
    for doc in results_cursor:
        print("\nQuery Result:", doc)
        found_results = True

    if not found_results:
        print(
            "\nNo documents found matching the criteria. 'total_sell_transactions' would be 0."
        )


except Exception as e:
    print(f"\nAn error occurred during MongoDB operation: {e}")

finally:
    # 4. Close the connection
    if client:
        client.close()
        print("\nMongoDB connection closed.")
