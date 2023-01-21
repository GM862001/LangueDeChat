# ===============================================
#                   config.py
# -----------------------------------------------
# This file defines the configuration variables.
# ===============================================

# ----------- KEYS -----------

INF = "INFORM"
REQ = "REQUEST"
GOAL_KEY = "doi"
AGT_INF_KEYS = [
    "authors",
    "document_title",
    "publication_title",
    "content_type",
    "publisher",
    "open_access",
    "publication_year",
    "abstract",
    "num_citations",
    GOAL_KEY
]
USR_INF_NUM_KEYS = [
    "publication_year",
    "min_publication_year",
    "max_publication_year",
    "min_num_citations"
]
USR_INF_STR_KEYS = [
    "authors",
    "document_title",
    "publication_title",
    "publisher",
    "keywords"
]
USR_INF_ENUM_KEYS = {
    "open_access": ["Yes", "No"],
    "content_type": ["Conferences", "Journals", "Books"]
}
# Dinstiction between numeric, string and enum keys is important for the EMC
USR_INF_KEYS = USR_INF_NUM_KEYS + USR_INF_STR_KEYS + list(USR_INF_ENUM_KEYS)
AGT_REQ_KEYS = USR_INF_KEYS
USR_REQ_KEYS = AGT_INF_KEYS
ALL_KEYS = list(set(AGT_INF_KEYS + USR_INF_KEYS))

# ----------- SPECIAL VALUES -----------

OWT = "ANYTHING"
MA = "MATCHING ALL"

# ----------- USER SIMULATOR -----------

USRSIM_INIT_INF = [] # Compulsory initial informs (if present in the user goal)
USRSIM_REQ_ONLY_AFTER_AGT_INF = [ # Only request after agent has proposed something
    "open_access", "publication_year", "num_citations", "content_type"
]

#----------- ACTIONS -----------

THX = "THANKS"
RJCT = "REJECT"
USR_SPEC_ACTS = [THX, RJCT]
NMA = "NO MATCH AVAILABLE"
WCP = "WITHDRAW CURRENT PROPOSALS"
AGT_SPEC_ACTS = [NMA, WCP]

AGT_ACTS = [(INF, key) for key in AGT_INF_KEYS]
AGT_ACTS += [(REQ, key) for key in AGT_REQ_KEYS]

