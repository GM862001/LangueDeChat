# -----------------------------------------------
# Generates the user simulator goals.
#
# Each goal is a dictionary with "inf" and "req" keys.
# The "inf" key represents the constraints for which
# the user wants to find a matching document, and is a 
# dictionary with the following structure:
# {
#     "keywords": "...",
#     "authors": "...",
#     "document_title": "...",
#     "publication_title": "...",
#     "publication_year": "...",
#     "publisher": "...",
#     "content_type": "...",
#     "open_access": "...",
#     "min_publication_year": "...",
#     "max_publication_year": "...",
#     "min_num_citations": "...",
# },
# where each key-value pair is actually optional.
# The "req" key represents the information that the
# user wants to retrieve from the matching document,
# and is a list of strings with the following values:
# [
#       "authors",
#       "document_title",
#       "publication_title",
#       "publication_year",
#       "publisher",
#       "content_type",
#       "open_access",
#       "num_citations",
#       "abstract",
#       "doi"
# ],
# where each string is actually optional.
# If a key is in the "inf" dictionary, then the
# it cannot be in the "req" list, and vice versa.
# -----------------------------------------------

import json
import random

from generate_knowledge_base import generating_keywords


if __name__ == "__main__":

    knowledge_base = json.load(open("data/knowledge_base.json"))

    user_goals = []

    while True:

        ref_doc = random.choice(knowledge_base) # Choose an existing document as a reference. This is done to generate realistic and achievable user goals.

        # Find a generating keyword in the reference document.
        # If no generating keyword is found, then the document is skipped.
        gen_keyword = None
        random.shuffle(generating_keywords)
        for gk in generating_keywords:
            context = ref_doc["document_title"] + ref_doc["publication_title"] + ref_doc["abstract"]
            if (context.lower()).find(gk.lower()) != -1:
                gen_keyword = gk
                break
        if not gen_keyword:
            continue

        informs = {}
        if random.random() < 0.8:
            informs["keywords"] = gen_keyword
        if random.random() < 0.4: # Inform only one author of the document
            informs["authors"] = ref_doc["authors"]
        if random.random() < 0.2:
            informs["document_title"] = ref_doc["document_title"]
        if random.random() < 0.1 or not informs: # At least one between "keywords", "authors", "document_title", and "publication_tilte" is required
            informs["publication_title"] = ref_doc["publication_title"]
        if random.random() < 0.1:
            informs["publisher"] = ref_doc["publisher"]
        if random.random() < 0.2:
            informs["content_type"] = ref_doc["content_type"]
        if ref_doc["open_access"] == "Yes" and random.random() < 0.8: # It does not make sense to inform "open_access": "No"
            informs["open_access"] = "Yes"
        if random.random() < 0.05:
            informs["publication_year"] = str(ref_doc["publication_year"])
        if "publication_year" not in informs:
            if random.random() < 0.2:
                informs["min_publication_year"] = str(ref_doc["publication_year"] - 1)
            if random.random() < 0.05:
                informs["max_publication_year"] = str(ref_doc["publication_year"] + 1)
        if random.random() < 0.3:
            informs["min_num_citations"] = str(ref_doc["num_citations"])

        requests = []
        if "authors" not in informs and random.random() < 0.8:
            requests.append("authors")
        if "document_title" not in informs and random.random() < 0.7:
            requests.append("document_title")
        if "publication_title" not in informs and random.random() < 0.4:
            requests.append("publication_title")
        if "publication_year" not in informs and random.random() < 0.6:
            requests.append("publication_year")
        if "publisher" not in informs and random.random() < 0.5:
            requests.append("publisher")
        if "content_type" not in informs and random.random() < 0.3:
            requests.append("content_type")
        if "open_access" not in informs and random.random() < 0.2:
            requests.append("open_access")
        if random.random() < 0.3:
            requests.append("abstract")
        if random.random() < 0.2:
            requests.append("num_citations")

        user_goal = {
            "INFORM": informs,
            "REQUEST": requests
        }
        user_goals.append(user_goal)
        if len(user_goals) == 10000:
            break


    with open("data/user_goals.json", "w") as user_goals_file:
        user_goals_file.write(json.dumps(user_goals))
