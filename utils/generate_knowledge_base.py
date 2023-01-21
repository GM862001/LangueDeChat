# -----------------------------------------------------------------
# Generates a knowledge base of documents using the IEEE Xplore API
#
# The knowledge base is a list of dictionaries,
# where each dictionary represents a document
# and has the following format:
# {
#     "authors": "author1, author2, ...",
#     "open_access": "Yes" or "No",
#     "document_title": "...",
#     "publication_title": "...",
#     "publisher": "...",
#     "content_type": "...",
#     "publication_year": "...",
#     "doi": "...",
#     "num_citations": "...",
#     "abstract": "..."
# }
# -----------------------------------------------------------------

import json

from ieee_api import query_ieee


def _remove_duplicates(knowledge_base):

    dois = set()
    for document in knowledge_base:
        if document["doi"] in dois:
            knowledge_base.remove(document)
        else:
            dois.add(document["doi"])


generating_keywords = [
    "Artificial intelligence",
    "Machine learning",
    "Neural networks",
    "Probabilistic models",
    "Intelligent agent",
    "Deep learning",
    "Search in complex environments", 
    "Constraint satisfaction problem",
    "Adversarial search",
    "Logical agents",
    "Probabilistic reasoning",
    "Knowledge representation",
    "Automated planning",
    "First order logic",
    "Search algorithms",
    "Multi-agent decision making",
    "Natural language processing",
    "Computer vision"
]
content_types = ["Journals", "Books", "Conferences"]


if __name__ == "__main__":

    knowledge_base = []

    for kw in generating_keywords:
        for content_type in content_types:
            for open_access in [True, False]:
                knowledge_base += query_ieee(kw, open_access, content_type)
                _remove_duplicates(knowledge_base)

    with open("data/knowledge_base.json", "w") as knowledge_base_file:
        knowledge_base_file.write(json.dumps(knowledge_base))
