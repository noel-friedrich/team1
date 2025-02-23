import os
import random

from addison import Addison
from brandon import Brandon
from database import Article, Database
from secret_keys import *
from william import William

# Create test_articles directory if it doesn't exist
os.makedirs("test_articles", exist_ok=True)

class Manager:
    def __init__(self, model_name="gpt-4o-mini", upload_online=False):
        self.upload_online = upload_online

        # init models
        self.william = William(model_name=model_name, history_size=3, temperature=0.85)
        self.brandon = Brandon(model_name=model_name, temperature=0.7)
        self.addison = Addison(model_name=model_name)

        # init database
        self.database = Database(MONGODB_ADDRESS, debug_messages=False)

        self.feedback = None

    def get_next_article(self) -> Article:
        addison_vetoes = True
        article = None
        backlinks_opportunities = []
        # Keep trying until Addison okays an article.
        while addison_vetoes:
            article = self.william.write_new_article(self.feedback)
            self.feedback = self.addison.write_feedback(self.database, article)
            backlinks_opportunities = self.brandon.identify_backlinks(article.content)
            addison_vetoes = "veto" in self.feedback.lower()

            # supplement feedback from allison with brandon
            random.shuffle(backlinks_opportunities)
            self.feedback += f"\n\nHere's a few suggestions from your friend Brandon for next possible article topics. If you were vetoed by Addison, you should follow one!\n"
            for i, backlink in enumerate(backlinks_opportunities):
                self.feedback += f"({i + 1}) {backlink}\n"
            if addison_vetoes:
                print(
                    f"Addison vetoed '{article.title}' and Brandon suggested {len(backlinks_opportunities)} topics.",
                    end="\n" * 2,
                )

        assert article is not None
        # export output
        print(f"William wrote about: {article.title!r}")
        self.database.upload_article(article, upload_online=self.upload_online)
        print(
            f"Addison accepted and Brandon suggested {len(backlinks_opportunities)} topics.",
            end="\n" * 2,
        )

        with open(
            os.path.join("test_articles", f"{article.title}.md"), "w", encoding="utf-8"
        ) as file:
            file.write(article.content)

        return article
