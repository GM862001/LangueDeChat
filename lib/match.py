# =============================================
#                    match.py
# ---------------------------------------------
# This file defines some functions to check
# if a document matches a set of constraints.
# =============================================

from collections import defaultdict
import re

from .config import OWT


CONSTRAINING_KEYS_MAPS = {
    "min_num_citations": (
        "num_citations", lambda num_cit, min_num_cit: int(num_cit) >= int(min_num_cit)
    ),
    "min_publication_year": (
        "publication_year", lambda year, min_year: int(year) >= int(min_year)
    ),
    "max_publication_year": (
        "publication_year", lambda year, max_year: int(year) <= int(max_year)
    )
}
CONSTRAINED_KEYS_MAPS = defaultdict(list)
for constraining_key, (constrained_key, f) in CONSTRAINING_KEYS_MAPS.items():
    CONSTRAINED_KEYS_MAPS[constrained_key].append((constraining_key, f))


def _find_words(context, key, value):

    if key not in context:
        return True
    for word in value.split():
        if context[key].find(word) == -1:
            return False
    return True


def _match_lambda(key, context, f, v):

    return (
        key not in context
        or f(context[key], v)
    )


def _match_authors(context, authors):

    return _find_words(context, "authors", authors)


def _match_document_title(context, doc_title):

    return _find_words(context, "document_title", doc_title)


def _match_publication_title(context, pub_title):

    return _find_words(context, "publication_title", pub_title)


def _match_publisher(context, publisher):

    return _find_words(context, "publisher", publisher)


def _match_keywords(context, keywords):

    return (
        _find_words(context, "abstract", keywords)
        or _find_words(context, "document_title", keywords)
        or _find_words(context, "publication_title", keywords)
    )


special_constraints = {
    "authors": _match_authors,
    "document_title": _match_document_title,
    "publication_title": _match_publication_title,
    "publisher": _match_publisher,
    "keywords": _match_keywords,
}


def _preprocess(dict):

    dict = {
        k: (
            v if isinstance(v, int)
            else int(v) if v.isdigit()
            else re.sub(r'[^\w\s]','', v).lower()
        ) for k, v in dict.items()
        if v != OWT
    }
    return dict


def get_conflict_keys(inform, context):

    """
    Get the keys in the given context that are in conflict with the given inform.

    Parameters
    ----------
    inform (dict) -> The inform dictionary to analyse. It may also be a document that has to be checked against the current constraints.
    context (dict) -> The context to analyse. It may be a set of agent proposals or constraints, or a document.

    Returns (set)
    -------------
    The set of keys in the given constraints that are in conflict with the given inform.

    """

    inform = _preprocess(inform)
    context = _preprocess(context)

    conflicting_keys = set()
    for inf_key, inf_value in inform.items():
        if inf_key in CONSTRAINING_KEYS_MAPS:
            constrained_key, f = CONSTRAINING_KEYS_MAPS[inf_key]
            if not _match_lambda(constrained_key, context, f, inf_value):
                conflicting_keys.add(constrained_key)
        if inf_key in CONSTRAINED_KEYS_MAPS:
            for constraining_key, f in CONSTRAINED_KEYS_MAPS[inf_key]:
                if not _match_lambda(
                    constraining_key,
                    context,
                    lambda x, y: f(y, x),
                    inf_value
                ):
                    conflicting_keys.add(constraining_key)
        if inf_key in special_constraints:
            if not special_constraints[inf_key](context, inf_value):
                conflicting_keys.add(inf_key)
        elif not _match_lambda(inf_key, context, lambda x, y: x == y, inf_value):
            conflicting_keys.add(inf_key)
    return conflicting_keys
