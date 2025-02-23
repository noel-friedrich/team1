from secret_keys import *
from william import William
from addison import Addison
from database import Database

database = Database(MONGODB_ADDRESS)

william = William(model_name="gpt-4o-mini", history_size=10, temperature=0.7)
addison = Addison(model_name="gpt-4o-mini")

num_articles = 100
feedback = None

for i in range(num_articles):
    article = william.write_new_article(feedback)
    feedback = addison.write_feedback(database, article)

    print(f"William wrote about: {article.title!r}")
    if "Veto" in feedback:
        print(f"Allison vetoed: {feedback}", end="\n" * 2)
    else:
        database.upload_article(article)
        print(f"Allison responded: {feedback}", end="\n" * 2)

    with open("articles.txt", "a", encoding="utf-8") as file:
        file.write(f"---------------------------------------------------------------\n\n{article.title}\n\n{article.content}\n\n")