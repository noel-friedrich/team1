import pymongo

class Article:

    def __init__(self, title, content):
        self.title = title
        self.content = content

class Database:

    def __init__(self, mongodb_address: str):
        # self.mongodb_client = pymongo.MongoClient(mongodb_address)
        # self.db = self.mongodb_client["william"]
        # self.articles_collection = self.db["articles"]
        self.fake_db_dict = {}

    def upload_article(self, article: Article):
        self.fake_db_dict[article.title] = article.content

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