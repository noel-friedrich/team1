import pymongo
from pymongo.operations import SearchIndexModel
from openai import OpenAI
from slugify import slugify
from datetime import datetime
from unsplash_client import UnsplashPhotoSearch

print(pymongo.__version__, pymongo.__file__)

class Article:

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __hash__(self):
        return hash(self.title)

class Vectorizer:

    def __init__(self):
        self.client = OpenAI()
        
    def get_embedding(self, text: str) -> list[float]:
        """Get embedding for a text using OpenAI's text-embedding-ada-002 model"""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

class Database:

    def __init__(self, mongodb_address: str, debug_messages=False):
        self.mongodb_client = pymongo.MongoClient(mongodb_address)
        self.db = self.mongodb_client["josh"]
        self.articles_collection = self.db["wikis"]
        self.vectorizer = Vectorizer()
        self.debug_messages = debug_messages
        self.unsplash_client = UnsplashPhotoSearch()

        self.backlink_opportunities: dict[Article, list[str]] = {}
        self.all_possible_backlinks: set[str] = set()
        self.reverse_backlink_map: dict[str, Article] = {}

        self.fake_db_dict = {}

    def upload_article(self, article: Article, upload_online=True):
        self.fake_db_dict[article.title] = article.content

        if not upload_online:
            return

        title_embedding = self.vectorizer.get_embedding(article.title)
        content_embedding = self.vectorizer.get_embedding(article.content)
        
        try:
            image_url = self.unsplash_client.search_photos(article.title)
            if not image_url:
                image_url = "https://picsum.photos/200"
                if self.debug_messages:
                    print(f"No Unsplash image found for '{article.title}', using fallback")
        except Exception as e:
            print(f"Error getting Unsplash image for '{article.title}': {e}")
            image_url = "https://picsum.photos/200"
        
        
        article_data = {
            "title": article.title,
            "content": article.content,
            "slug": slugify(article.title) or f"untitled-{datetime.now()}",
            "image_url": image_url,
            "createdAt": datetime.now(),
            "metadata": {
                "model": "gpt-4o-mini",
                "thread_id": "abc123" # doesn't really matter at this point
            },
            "votes": 1,
            # Add vector embeddings
            "title_embedding": title_embedding,
            "content_embedding": content_embedding
        }


        self.upload_article_data(article_data)

    def upload_article_data(self, article_data):
        try:
            # Insert and get the inserted ID
            result = self.articles_collection.insert_one(article_data)
            
            # Create vector search index if it doesn't exist
            try:
                index_definition = {
                    "mappings": {
                        "fields": [
                            {
                                "type": "vector",
                                "path": "title_embedding",
                                "numDimensions": 1536,
                                "similarity": "dotProduct"
                                # "quantization": "scalar"  # Remove if your Atlas version doesn't support it
                            },
                            {
                                "type": "vector",
                                "path": "content_embedding",
                                "numDimensions": 1536,
                                "similarity": "dotProduct"
                            }
                        ]
                    }
                }
                self.articles_collection.create_search_index(
                    "vector_index",
                    SearchIndexModel(
                        name="vector_index",
                        definition=index_definition
                    )
                )
            except Exception as e:
                # Index might already exist
                if self.debug_messages:
                    print(f"Note: Vector index creation attempt: {str(e)}")
            
            # Verify the insertion by fetching the document
            inserted_doc = self.articles_collection.find_one({"_id": result.inserted_id})
            if self.debug_messages:
                print("\n=== MongoDB Insertion Test ===")
                print(f"Document inserted with ID: {result.inserted_id}")
                print(f"Verification - Found document title: {inserted_doc['title']}")
                print(f"Document timestamp: {inserted_doc['createdAt']}")
                print("Vector embeddings added for title and content")
                print("===========================\n")
            
        except pymongo.errors.PyMongoError as e:
            if self.debug_messages:
                print(f"MongoDB Error: {str(e)}")

    def query_titles(self, query: str) -> str:
        tokens = query.lower().split(" ")
        written_articles = list(self.fake_db_dict.keys())
        matches = [
            article for article in written_articles
            if any(token in article.lower() for token in tokens)
        ]
        if len(matches) == 0:
            return "No articles with similar name found."
        return "\n".join(matches)