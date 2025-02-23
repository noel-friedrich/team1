from secret_keys import *
from william import William
from addison import Addison
from database import Database

database = Database(MONGODB_ADDRESS)

william = William(model_name="gpt-4o-mini", history_size=10)
addison = Addison(model_name="gpt-4o-mini")

num_articles = 10
feedback = None

for i in range(num_articles):
    article = william.write_new_article(feedback)
    feedback = addison.write_feedback(database, article)
    database.upload_article(article)

    print(f"William wrote about: {article.title!r}")
    print(f"Allison responded: {feedback}", end="\n" * 2)