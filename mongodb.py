import pymongo
from datetime import datetime
from slugify import slugify

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://george:hack1r3land@cluster0.uf8bs.mongodb.net/")  # Replace with your MongoDB URI
db = client["william"]
articles_collection = db["articles"]

# Test data
test_article = {
    "title": "Test Article",
    "slug": slugify("Test Article"),
    "content": "This is a test article content.",
    "image_url": "https://example.com/hello-world.jpg",
    "timestamp": datetime.now(),
    "metadata": {
        "model": "gpt-4-mini",
        "thread_id": "test_thread_123"
    },
    "votes": 5,
    "sequence": 1,
}

try:
    # Insert test document
    result = articles_collection.insert_one(test_article)
    
    # Verify the insertion
    inserted_doc = articles_collection.find_one({"_id": result.inserted_id})
    print("\n=== MongoDB Test Connection ===")
    print(f"Document inserted with ID: {result.inserted_id}")
    print(f"Verification - Found document title: {inserted_doc['title']}")
    print(f"Document timestamp: {inserted_doc['timestamp']}")
    print("===========================\n")
    
except pymongo.errors.PyMongoError as e:
    print(f"MongoDB Error: {str(e)}")

# Optional: Clean up test data
# articles_collection.delete_one({"_id": result.inserted_id})
