# export_to_json.py
import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.json_util import dumps


def export_db_to_json(output_file="sample_analytics.json"):
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("🔴 MONGODB_URI not found in .env")

    client = MongoClient(uri)
    db = client["sample_analytics"]

    full_data = {}
    for coll_name in db.list_collection_names():
        docs = list(db[coll_name].find({}))
        # dumps handles BSON types properly :contentReference[oaicite:1]{index=1}
        json_str = dumps(docs, indent=2)
        full_data[coll_name] = json.loads(json_str)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)

    client.close()
    print(f"✅ Exported {len(full_data)} collections to '{output_file}'")


if __name__ == "__main__":
    try:
        export_db_to_json()
    except Exception as e:
        print("Error:", e)
