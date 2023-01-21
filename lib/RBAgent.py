import random

from .config import (
    AGT_INF_KEYS, AGT_REQ_KEYS, AGT_SPEC_ACTS, AGT_ACTS, WCP,
    USR_SPEC_ACTS, RJCT, INF, REQ, OWT, GOAL_KEY
)
from .match import get_conflict_keys, CONSTRAINED_KEYS_MAPS


class RBAgent():

    """
    Rule-based agent.

    Attributes
    ----------
    _curr_agt_inf : dict
        The set of keys that the agent has informed.
    _curr_usr_inf : dict
        The set of keys that the user has informed.
    _curr_OWT_inf : set
        The set of keys that the user has informed with OWT value.
    _pending_usr_req : set
        The set of the pending user requests.
    _action : tuple
        The current action.

    Methods
    -------
    reset()
        Reset the agent.
    record_processed_action(action)
        Update the agent state after the action has been processed by the state tracker.
    _reset_agent_informs()
        Reset the current agent informs.
    get_action(user_action)
        Get the agent action given the user action.

    """

    def __init__(self):

        self.reset()


    def reset(self):

        """
        Reset the agent.

        """

        # Internal state variables
        self._curr_agt_inf = {}
        self._curr_usr_inf = {}
        self._curr_OWT_inf = set()
        self._curr_usr_req = set()
        self._pending_usr_req = set()


    def record_processed_action(self, action):

        """
        Update the agent state after the action has been processed by the state tracker.

        Parameters
        ----------
        action : tuple or string
            The value of the informed key.

        """

        if action == WCP:
            self._reset_agent_informs()
        elif action not in AGT_SPEC_ACTS and action[0] == INF:
            self._curr_agt_inf[action[1]] = action[2]


    def _reset_agent_informs(self):

        """
        Reset the current agent informs.

        """

        self._curr_agt_inf = {}
        self._pending_usr_req = self._curr_usr_req.copy()


    def get_action(self, user_action):

        """
        Get the agent action given the user action.

        Parameters
        ----------
        user_action : dict or string
            The user action.

        Returns
        -------
        tuple
            The agent action.

        """

        # PROCESS USER ACTION

        # If the user rejects or inform about something that is in conflict
        # with the current agent proposals, reset them
        if user_action == RJCT:
            self._reset_agent_informs()
        elif user_action not in USR_SPEC_ACTS:
            if get_conflict_keys(user_action[INF], self._curr_agt_inf):
                self._reset_agent_informs()
            # Update the state of the agent
            self._curr_usr_inf.update(user_action[INF])
            self._curr_usr_req.update(user_action[REQ])
            self._pending_usr_req.update(user_action[REQ])
            self._curr_usr_req.difference_update(user_action[INF])
            self._pending_usr_req.difference_update(user_action[INF])
            OWT_keys = [k for k, v in user_action[INF].items() if v == OWT]
            not_OWT_keys = {k for k, v in user_action[INF].items() if v != OWT}
            self._curr_OWT_inf.update(OWT_keys)
            self._curr_OWT_inf.difference_update(not_OWT_keys)

        # ----------------------------

        # GET AGENT ACTION

        # 1) If the user requests a key, inform the same key;
        # 2) Else if the user has pending requests, inform it about one of them;
        # 3) Else choose a random action among the following options:
        #   3.1) Inform the goal key, if not already informed;
        #   3.2) Request a not yet informed key;
        #   3.3) Inform a not yet informed key.
        # If none of the above was possible,
        # choose a random action among the following:
        #   3.4) Inform an key which was informed with OWT value;
        #   3.5) Request a random key.
        if user_action not in USR_SPEC_ACTS and user_action[REQ]:  # 1)
            self._action = (INF, random.choice(list(user_action[REQ])))
        elif self._pending_usr_req:  # 2)
            self._action = (INF, random.choice(list(self._pending_usr_req)))
        else:  # 3)
            already_inf = self._curr_agt_inf | self._curr_usr_inf
            irrelevant_keys = set(already_inf)
            for k in already_inf:
                if k in CONSTRAINED_KEYS_MAPS:
                    constraining_keys = [
                        ck for ck, _ in CONSTRAINED_KEYS_MAPS[k]
                    ]
                    irrelevant_keys.update(constraining_keys)
            req_keys = [k for k in AGT_REQ_KEYS if k not in irrelevant_keys]
            inf_keys = [k for k in AGT_INF_KEYS if k not in irrelevant_keys]
            inf_OWT_keys = [k for k in self._curr_OWT_inf if k in AGT_INF_KEYS]
            if GOAL_KEY in inf_keys and random.random() < 1 / 3:  # 3.1)
                self._action = (INF, GOAL_KEY)
            elif req_keys and random.random() < 1 / 2:  # 3.2)
                self._action = (REQ, random.choice(req_keys))
            elif inf_keys:  # 3.3)
                self._action = (INF, random.choice(inf_keys))
            elif inf_OWT_keys and random.random() < 1 / 2:  # 3.4)
                self._action = (INF, random.choice(inf_OWT_keys))
            else:  # 3.5)
                self._action = (REQ, random.choice(AGT_REQ_KEYS))
        # Update the state of the agent
        if self._action[0] == INF:
            self._pending_usr_req.discard(self._action[1])
        return AGT_ACTS.index(self._action), self._action

        # ----------------------------
