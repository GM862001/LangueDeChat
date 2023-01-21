from collections import defaultdict
import random
import json

from .match import get_conflict_keys
from .config import GOAL_KEY, NMA, OWT, MA


class KBManager:

    """
    Knowledge Base Manager.

    Attributes
    ----------
    _kb : list of dictionaries
        The knowledge base.
    _cache : dict
        The cache of the knowledge base manager.

    Methods
    -------
    find_matching_docs(constraints)
        Find the documents which match the given constraints.
    find_matching_value(key, constraints)
        Find a matching value for the given key, given the constraints.
    count_matches(constraints)
        Count the number of matches for each given constraint key.
    check_goal_proposal_consistency(goal_proposal, constraints)
        Compare a goal proposal with a set of constraints.
    get_kb_size()
        Get the size of the knowledge base.

    """

    def __init__(self, kb_filepath):

        """
        Parameters
        ----------
        kb_filepath : str
            The path to the knowledge base file.

        """

        with open(kb_filepath) as kb_file:
            self._kb = json.load(kb_file)
        self._cache = {
            "documents": defaultdict(list),
            "values": defaultdict(list),
            "count": defaultdict(dict)
        }


    def find_matching_docs(self, constraints):

        """
        Find the documents which match the given constraints.

        Parameters
        ----------
        constraints : dict
            The constraints to match.

        Returns (list of dictionaries)
        ------------------------------
        The documents which match the given constraints.

        """

        hashable_constraints = frozenset(constraints.items())
        if not self._cache["documents"][hashable_constraints]:
            self._cache["documents"][hashable_constraints] = [
                doc for doc in self._kb
                if not get_conflict_keys(constraints, doc)
            ]
        return self._cache["documents"][hashable_constraints]


    def find_matching_value(self, key, constraints):

        """
        Find a matching value for the given key, given the constraints.

        Parameters
        ----------
        key : str
            The key for which to find a matching value, given the constraints.
        constraints : dict
            The constraints to match.

        Returns
        -------
        str
            A matching value for the given key.
            If more than one match is found, a random one is selected.
            If no matching values are found, return NMA value.

        """

        hashable_constraints = frozenset(constraints.items())
        if not self._cache["values"][(key, hashable_constraints)]:
            documents = self.find_matching_docs(constraints)
            if not documents:
                self._cache["values"][(key, hashable_constraints)] = [NMA]
            else:
                self._cache["values"][(key, hashable_constraints)] = [
                    str(doc[key]) for doc in documents
                ]
        return random.choice(
            self._cache["values"][(key, hashable_constraints)]
        )


    def count_matches(self, constraints):

        """

        Count the number of matches for each given constraint key.

        Parameters
        ----------
        constraints : dict
            The constraints to match.

        Returns
        -------
        dict
            A dictionary whose keys are the same of the given constraints,
            plus a MA key,and whose values are the number of documents in
            the database which match that specific constraint. The value of MA
            key is the number of documents which match all constraints.

        """

        hashable_constraints = frozenset(constraints.items())
        if not self._cache["count"][hashable_constraints]:
            match_dict = {}
            match_dict[MA] = len(self.find_matching_docs(constraints))
            for k, v in constraints.items():
                match_dict[k] = (
                    len(self._kb) if v == OWT
                    else len(self.find_matching_docs({k: v}))
                )
            self._cache["count"][hashable_constraints] = match_dict
        return self._cache["count"][hashable_constraints]


    def check_goal_proposal_consistency(self, goal_proposal, constraints):

        """
        Compare a goal proposal with a set of constraints.

        Parameters
        ----------
        goal_proposal : str
            The goal proposal to be compared.
        constraints : dict
            The constraints that the goal proposal must match.

        Returns
        -------
        bool
            Whether the goal proposal matches the constraints or not.

        """
        
        constraint = {GOAL_KEY : goal_proposal}
        proposed_doc, = self.find_matching_docs(constraint)
        return not get_conflict_keys(constraints, proposed_doc)


    def get_kb_size(self):

        """
        Get the size of the knowledge base.

        Returns
        -------
        int
            The size of the knowledge base.

        """

        return len(self._kb)