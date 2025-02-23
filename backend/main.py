from secret_keys import *
from william import William
from addison import Addison
from brandon import Brandon
from database import Database
import os, random

# init database
database = Database(MONGODB_ADDRESS, debug_messages=False)

# init models
william = William(model_name="gpt-4o-mini", history_size=4, temperature=0.85)
brandon = Brandon(model_name="gpt-4o-mini", temperature=0.7)
addison = Addison(model_name="gpt-4o-mini")

feedback = None
for i in range(9999999):
    # write article, make addison judge and brandon identify
    article = william.write_new_article(feedback)
    feedback = addison.write_feedback(database, article)
    backlinks_opportunities = brandon.identify_backlinks(article.content)
    alice_vetoes = "veto" in feedback.lower()

    # supplement feedback from allison with brandon
    random.shuffle(backlinks_opportunities)
    feedback += f"\n\nHere's a few suggestions from your friend Brandon for next possible article topics. If you were vetoed by Addison, you should follow one!\n"
    for i, backlink in enumerate(backlinks_opportunities):
        feedback += f"({i + 1}) {backlink}\n"

    # export output
    print(f"William wrote about: {article.title!r}")
    if alice_vetoes:
        print(f"Addison vetoed and Brandon suggested {len(backlinks_opportunities)} topics.", end="\n" * 2)
    else:
        database.upload_article(article, upload_online=False)
        print(f"Addison accepted and Brandon suggested {len(backlinks_opportunities)} topics.", end="\n" * 2)

        with open(os.path.join("test_articles", f"{article.title}.md"), "w", encoding="utf-8") as file:
            file.write(article.content)