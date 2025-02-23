from secret_keys import *
from william import William
from addison import Addison
from database import Database

import subprocess

database = Database(MONGODB_ADDRESS)

william = William(model_name="gpt-4o-mini", history_size=10)
addison = Addison(model_name="gpt-4o-mini")

num_articles = 20
feedback = None

for i in range(num_articles):
    article = william.write_new_article(feedback)
    feedback = addison.write_feedback(database, article)
    database.upload_article(article)

    with open(f"test_articles/article{i:03}.txt", "w", encoding="utf-8") as file:
        file.write(article.content)

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"added test article about {article.title}"], check=True)
    print(i + 1, article.title)