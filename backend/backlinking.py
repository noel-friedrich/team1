from database import Article, Database
from secret_keys import *

import numpy as np
import random
from sentence_transformers import SentenceTransformer
from functools import cache

# init database

def cosine_similarity(vec1, vec2):
    """
    Calculate the cosine similarity between two vectors.

    Parameters:
    vec1 (numpy.ndarray): First vector.
    vec2 (numpy.ndarray): Second vector.

    Returns:
    float: Cosine similarity between vec1 and vec2.
    """
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

@cache
def vectorize(sentence, model):
    embeddings = model.encode(sentence)
    return np.array(embeddings)

def backlinking_round(database: Database, batch_size=50, debug_print=False):
    if debug_print:
        print(f"Starting Backlinking round with {batch_size=}")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    all_articles: list[Article] = database.get_all_articles()
    random.shuffle(all_articles)
    all_articles = all_articles[:batch_size]

    articles_map = {a.title: a.content for a in all_articles}
    article_article_map = {a.title: a for a in all_articles}

    if debug_print:
        print(f"Loaded {len(all_articles)} articles.")

    title_vectors: dict[str, np.array] = {}
    for i, title in enumerate(articles_map.keys()):
        title_vectors[title] = vectorize(title, model)
    if debug_print:
        print("Done with vectorizing the titles.")

    def tokenize(sentence: str) -> list[str]:
        return sentence.replace(".", "").replace("!", "").replace("?", "").replace(",", "").split(" ")

    article_backlinks: dict[str, list[str]] = {}
    all_titles = list(articles_map.keys())
    title_tokenizations = {t: tokenize(t) for t in all_titles}
    single_word_titles = [t for t in all_titles if len(title_tokenizations[t]) == 1]

    similarity_thresh = 0.8

    def parse_article(title1: str, content: str):
        words = tokenize(content)
        backlinks: dict[str, str] = {}

        # find 1 word matches
        for word in words:
            word_vec = vectorize(word, model)
            for title in single_word_titles:
                if title == title1:
                    continue
                title_vec = title_vectors[title]
                if cosine_similarity(word_vec, title_vec) >= similarity_thresh:
                    backlinks[word] = title

        # find 2 word matches
        for word, next_word in zip(words, words[1:]):
            query = f"{word} {next_word}"
            query_vec = vectorize(word, model)
            for title in all_titles:
                if title == title1:
                    continue
                title_vec = title_vectors[title]
                if cosine_similarity(query_vec, title_vec) >= similarity_thresh:
                    backlinks[query] = title

        return backlinks

    for i, title in enumerate(articles_map.keys()):
        content = articles_map[title]
        backlinks = parse_article(title, content)
        article_backlinks[title] = backlinks

        if debug_print:
            print(f"{i + 1} done", end="\r")

    all_backlinks: dict[Article, tuple[str, str]] = {}

    for article in all_articles:
        if article.backlinks == "":
            continue
        backlinks = {b.split(":")[0]: b.split(":")[1] for b in article.backlinks.split(",")}
        all_backlinks[article] = backlinks

    for title in all_titles:
        article = article_article_map[title]
        backlinks = {k: article_article_map[t].uid for k, t in article_backlinks[title].items()}
        if not article in all_backlinks:
            all_backlinks[article] = {}
        for k, v in backlinks.items():
            all_backlinks[article][k] = v

    if debug_print:
        print("Finished entirely.")

    return all_backlinks

if __name__ == "__main__":
    while True:
        database = Database(MONGODB_ADDRESS, debug_messages=False)
        all_backlinks = backlinking_round(database, 50, True)
        for article, backlinks in all_backlinks.items():
            database.update_article_backlinks(article.uid, backlinks)
        print()