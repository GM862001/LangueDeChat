import requests


IEEE_SITE = 'https://ieeexploreapi.ieee.org/api/v1/search/articles'
IEEE_API_KEY = 'h2ky67htcwsbyabjvxhemm75'
IEEE_HEADERS = 'apikey=' + IEEE_API_KEY
SPACE_IEEE = "%20"
QUOTES_IEEE = "%22"
QUERYTEXT_CONJ = SPACE_IEEE + "AND" + SPACE_IEEE


def _compose_ieee_link(keywords, open_access, content_type, max_records):

    """
    Compose the link to be used to query the IEEE API.

    Parameters
    ----------
    keywords (str) -> The query keywords.
    open_access (bool) -> Whether to return only open access documents.
    content_type (str) -> The type of documents to be returned by the query.
    max_records (int) -> The maximum number of records to be returned by the query.

    Returns (str)
    -------------
    Link to be used to query the IEEE API.

    """

    return (
        f"{IEEE_SITE}?max_records={max_records}&open_access={open_access}&"
        f"querytext=({QUOTES_IEEE}All{SPACE_IEEE}Metadata{QUOTES_IEEE}:{keywords})"
        f"{QUERYTEXT_CONJ}({QUOTES_IEEE}ContentType{QUOTES_IEEE}:{content_type})"
        f"&{IEEE_HEADERS}"
    )


def _make_ieee_request(keywords, open_access, content_type, max_records):

    """
    Query the IEEE API.

    Parameters
    ----------
    keywords (str) -> The query keywords.
    max_records (int) -> The maximum number of records to be returned by the query.
    open_access (bool) -> Whether to return only open access documents.
    content_type (str) -> The type of documents to be returned by the query.

    Returns (list of dict)
    ----------------------
    The result of the query as a list of documents.

    """

    ieee_request = _compose_ieee_link(keywords, open_access, content_type, max_records)
    ieee_response = requests.get(ieee_request).json()
    return ieee_response["articles"] if ieee_response["total_records"] > 0 else []


def _preprocess(documents):

    """
    Preprocess a list of documents.

    Parameters
    ----------
    documents (list of dict) -> Documents as provided by IEEE API.

    Returns (list of dict)
    ----------------------
    Preprocessed documents.

    Notes
    -----
    We want the preprocessed documents to have the following format:
    {
        "authors": "author1, author2, ...",
        "open_access": "Yes" or "No",
        "document_title": "...",
        "publication_title": "...",
        "publisher": "...",
        "content_type": "...",  
        "publication_year": "...",
        "doi": "...",
        "num_citations": "...",
        "abstract": "..."
    }

    """

    preprocessed_documents = []

    for doc in documents:
        # If any of the fields is missing in the original document, we skip it
        try:
            preprocessed_doc = {}
            preprocessed_doc["authors"] = ", ".join([author["full_name"] for author in doc["authors"]["authors"]])
            preprocessed_doc["open_access"] = "Yes" if "access_type" in doc and doc["access_type"] == "OPEN_ACCESS" else "No"
            preprocessed_doc["document_title"] = doc["title"]
            preprocessed_doc["num_citations"] = doc["citing_paper_count"]
            for key in ["publication_title", "publisher", "content_type", "publication_year", "doi", "abstract"]:
                preprocessed_doc[key] = doc[key]
            for value in preprocessed_doc.values():
                if not value:
                    raise Exception
            preprocessed_documents.append(preprocessed_doc)
        except:
            continue

    return preprocessed_documents


def query_ieee(keywords, open_access, content_type, max_records=200):

    """
    Query the IEEE API and returns the cleaned result.

    Parameters
    ----------
    keywords (str) -> The query keywords.
    max_records (int) -> The maximum number of records to be returned by the query.
    open_access (bool) -> Whether to return only open access documents.
    content_type (str) -> The type of documents to be returned by the query.

    Returns (list of dict)
    ----------------------
    The cleaned result of the query as a list of documents.

    """

    documents = _make_ieee_request(keywords, open_access, content_type, max_records)
    return _preprocess(documents)