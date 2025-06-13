from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def get_active_customers():
    # MongoDB connection details
    mongo_host = "localhost"
    mongo_port = 27017
    mongo_db = "mydatabase"
    mongo_collection = "customers"

    try:
        # Establish MongoDB connection
        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[mongo_db]
        collection = db[mongo_collection]

        # Query to find all active customers
        query = {"active": True}

        # Execute the query
        active_customers = list(collection.find(query))

        # Close the connection
        client.close()

        return active_customers

    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None


# Get the active customers
active_customers = get_active_customers()

# Print the results (for demonstration purposes)
if active_customers:
    for customer in active_customers:
        print(customer)
else:
    print("No active customers found or could not connect to the database.")
