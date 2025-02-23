from database import Article, Database
from secret_keys import *

import numpy as np
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

    all_articles: list[Article] = database.get_all_articles()[:batch_size]
    articles_map = {a.title: a.content for a in all_articles}

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

    def parse_article(title: str, content: str):
        words = tokenize(content)
        backlinks: list[tuple[str, str]] = []

        # find 1 word matches
        for word in words:
            word_vec = vectorize(word, model)
            for title in single_word_titles:
                title_vec = title_vectors[title]
                if cosine_similarity(word_vec, title_vec) >= similarity_thresh:
                    backlinks.append((word, title))

        # find 2 word matches
        for word, next_word in zip(words, words[1:]):
            query = f"{word} {next_word}"
            query_vec = vectorize(word, model)
            for title in all_titles:
                title_vec = title_vectors[title]
                if cosine_similarity(query_vec, title_vec) >= similarity_thresh:
                    backlinks.append((query, title))

        return backlinks

    for i, title in enumerate(articles_map.keys()):
        content = articles_map[title]
        backlinks = parse_article(title, content)
        article_backlinks[title] = backlinks

        if debug_print:
            print(f"{i + 1} done", end="\r")

    if debug_print:
        print("Finished entirely.")

    print()
    print(article_backlinks)

if __name__ == "__main__":
    database = Database(MONGODB_ADDRESS, debug_messages=False)
    backlinking_round(database, 50, True)