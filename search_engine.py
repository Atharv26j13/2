"""
Mini Search Engine - NLP Activity 8 (full solution)
Grades 8-12 | Python 3, standard library only

Search engines don't read every page when you search. They build an INDEX
in advance (like the index at the back of a book), then use maths to rank
the pages. Three rankers battle it out here:
  1. COUNT   - how many times do the query words appear?
  2. TF      - what FRACTION of the article is query words?
  3. TF-IDF  - like TF, but rare words matter more than common ones
"""
import math
from collections import Counter, defaultdict
from articles import ARTICLES


# ---------------------------------------------------------------
# Step 1 (given): text -> lowercase words
# ---------------------------------------------------------------
def tokenize(text):
    chars = [ch if ch.isalnum() else " " for ch in text.lower()]
    return "".join(chars).split()


# ---------------------------------------------------------------
# Step 2: Build the inverted index
#   index["honey"] = {6: 4}   ->  article 6 contains "honey" 4 times
#   lengths[6] = 74           ->  article 6 has 74 words
# ---------------------------------------------------------------
def build_index(articles):
    index = defaultdict(dict)
    lengths = {}
    for doc_id, (title, text) in enumerate(articles):
        words = tokenize(title + " " + text)
        lengths[doc_id] = len(words)
        for word in words:
            index[word][doc_id] = index[word].get(doc_id, 0) + 1
    return index, lengths


INDEX, LENGTHS = build_index(ARTICLES)
N = len(ARTICLES)


# ---------------------------------------------------------------
# Step 3: Three ways to score. Each only visits articles that contain
#         the word, thanks to the index (that's why search is fast!)
# ---------------------------------------------------------------
def score_count(query):
    scores = Counter()
    for term in tokenize(query):
        for doc_id, count in INDEX.get(term, {}).items():
            scores[doc_id] += count
    return scores


def score_tf(query):
    scores = Counter()
    for term in tokenize(query):
        for doc_id, count in INDEX.get(term, {}).items():
            scores[doc_id] += count / LENGTHS[doc_id]
    return scores


def idf(term):
    """Rare words get a big number; a word in EVERY article gets 0."""
    docs_with_term = len(INDEX.get(term, {}))
    if docs_with_term == 0:
        return 0
    return math.log(N / docs_with_term)


def score_tfidf(query):
    scores = Counter()
    for term in tokenize(query):
        for doc_id, count in INDEX.get(term, {}).items():
            scores[doc_id] += count / LENGTHS[doc_id] * idf(term)
    return scores


RANKERS = {"COUNT": score_count, "TF": score_tf, "TF-IDF": score_tfidf}


def search(query, ranker="TF-IDF", k=3):
    scores = RANKERS[ranker](query)
    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    return [(ARTICLES[doc_id][0], score) for doc_id, score in ranked[:k] if score > 0]


# ---------------------------------------------------------------
# Step 4 (given): show the best sentence with the query words in CAPS
# ---------------------------------------------------------------
def snippet(title, query, bold=False):
    text = dict(ARTICLES)[title]
    terms = set(tokenize(query))
    sentences = text.replace("; ", ". ").split(". ")
    best = max(sentences, key=lambda s: sum(idf(w) for w in set(tokenize(s)) & terms))
    marked = []
    for word in best.split():
        if word.lower().strip(".,;:") in terms:
            word = f"**{word}**" if bold else word.upper()
        marked.append(word)
    return " ".join(marked)


# ---------------------------------------------------------------
# Step 5: Search Engine Wars! You decided the right answer for each query.
# ---------------------------------------------------------------
JUDGED_QUERIES = [
    ("the history of pizza", "The History of Pizza"),
    ("red planet rover", "Mars Rovers"),
    ("how do bees make honey", "Honey Bees"),
    ("the moon and the earth", "The Moon"),
    ("chess world champion", "Chess"),
    ("cricket bat and ball", "Cricket"),
    ("where does chocolate come from", "Chocolate"),
    ("the colours of the rainbow", "How Rainbows Form"),
    ("lava from a volcano", "Volcanoes"),
    ("dinosaur fossils", "Dinosaurs"),
]


def wars():
    print(f"{'query':<32}" + "".join(f"{name:<24}" for name in RANKERS))
    wins = Counter()
    for query, right in JUDGED_QUERIES:
        row = f"{query:<32}"
        for name in RANKERS:
            results = search(query, name, k=1)
            top = results[0][0] if results else "(nothing)"
            ok = top == right
            wins[name] += ok
            row += f"{('OK ' if ok else 'XX ') + top[:20]:<24}"
        print(row)
    print(f"{'WINS':<32}" + "".join(f"{f'{wins[n]}/{len(JUDGED_QUERIES)}':<24}" for n in RANKERS))


def index_report():
    print(f"Index: {len(INDEX)} different words across {N} articles\n")
    print("Words found in the MOST articles (lowest IDF):")
    for word, posting in sorted(INDEX.items(), key=lambda kv: -len(kv[1]))[:5]:
        print(f"   {word:<8} in {len(posting):>2}/{N} articles   idf = {idf(word):.2f}")


# Queries that beat EVERY ranker. What would a real search engine do?
BREAK_IT = ["dinosaur", "game", "sweet food", "the"]


if __name__ == "__main__":
    index_report()
    print()
    wars()
    print("\nBreak it:")
    for query in BREAK_IT:
        found = [title for title, _ in search(query, k=3)]
        print(f"   {query!r:<13} -> {found or 'nothing found'}")
    print("\nYour turn ('quit' to stop)")
    while True:
        query = input("\n> ")
        if query.strip().lower() == "quit":
            break
        for rank, (title, score) in enumerate(search(query), 1):
            print(f"  {rank}. {title}  (score {score:.3f})")
            print(f"     ...{snippet(title, query)}...")
