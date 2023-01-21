import numpy as np

from .KBManager import KBManager
from .config import (
    USR_SPEC_ACTS, USR_INF_KEYS, USR_REQ_KEYS, RJCT,
    AGT_SPEC_ACTS, AGT_INF_KEYS, AGT_REQ_KEYS, WCP, NMA,
    ALL_KEYS, INF, REQ, MA, OWT
)
from .match import get_conflict_keys


class StateTracker:

    """
    State tracker.

    Attributes
    ----------
    _kb_manager (KBManager) -> The knowledge base manager.
    _curr_agt_inf (dict) -> The current agent_informs.
    _curr_usr_inf (dict) -> The current user informs.
    _curr_usr_req (set) -> The current user requests.
    _curr_constraints (dict) -> The current constraints.
    _last_agt_act (tuple or str) -> The last agent action.
    _last_usr_act (dict or string) -> The last user action.

    Methods
    -------
    reset()
        Reset the state tracker.
    get_state()
        Get the state representation for the RL agent.
    get_state_dim()
        Get the state dimension.
    _reset_agent_informs():
        Reset the current agent informs.
    process_user_action(user_action)
        Update the state tracker internal state given the user action.
    process_agent_action(agent_action)
        Process the agent action and update the state tracker internal state.

    """

    def __init__(self, kb_filepath):

        """
        Parameters
        ----------
        kb_filepath (KBManager) -> The path to the knowledge base file.

        """

        self._kb_manager = KBManager(kb_filepath)
        self.reset()


    def reset(self):

        """
        Reset the state tracker.

        """

        # Internal state variables
        self._curr_agt_inf = {}
        self._curr_usr_inf = {}
        self._curr_constraints = {}
        self._curr_usr_req = set()
        self._last_agt_act = None
        self._last_usr_act = None


    def get_state(self):

        """
        Get the state representation for the RL agent.

        Returns (numpy array)
        ---------------------
        The state representation.

        """

        # Current user informs and requests onehot representation
        curr_usr_inf_rep = np.zeros(len(USR_INF_KEYS))
        curr_usr_req_rep = np.zeros(len(USR_REQ_KEYS))
        for key in self._curr_usr_inf:
            curr_usr_inf_rep[USR_INF_KEYS.index(key)] = 1
        for key in self._curr_usr_req:
            curr_usr_req_rep[USR_REQ_KEYS.index(key)] = 1

        # Current agent informs onehot representation
        curr_agt_inf_rep = np.zeros(len(AGT_INF_KEYS))
        for key in self._curr_agt_inf:
            curr_agt_inf_rep[AGT_INF_KEYS.index(key)] = 1

        # Last user action onehot representation
        last_usr_act_rep = np.zeros(len(USR_SPEC_ACTS))
        last_usr_act_inf_rep = np.zeros(len(USR_INF_KEYS))
        last_usr_act_req_rep = np.zeros(len(USR_REQ_KEYS))
        if self._last_usr_act:
            if self._last_usr_act in USR_SPEC_ACTS:
                last_usr_act_rep[USR_SPEC_ACTS.index(self._last_usr_act)] = 1
            else:
                for key in self._last_usr_act[INF]:
                    last_usr_act_inf_rep[USR_INF_KEYS.index(key)] = 1
                for key in self._last_usr_act[REQ]:
                    last_usr_act_req_rep[USR_REQ_KEYS.index(key)] = 1

        # Last agent action onehot representation
        last_agt_act_rep = np.zeros(len(AGT_SPEC_ACTS))
        last_agt_act_inf_rep = np.zeros(len(AGT_INF_KEYS))
        last_agt_act_req_rep = np.zeros(len(AGT_REQ_KEYS))
        if self._last_agt_act in AGT_SPEC_ACTS:
            last_agt_act_rep[AGT_SPEC_ACTS.index(self._last_agt_act)] = 1
        elif self._last_agt_act:
            intent, key = self._last_agt_act[0:2]
            if intent == INF:
                last_agt_act_inf_rep[AGT_INF_KEYS.index(key)] = 1
            else:
                last_agt_act_req_rep[AGT_REQ_KEYS.index(key)] = 1

        # Knowledge base matches counts absolute and boolean representations
        expanded_keys = ALL_KEYS + [MA]
        kb_count_abs_rep, kb_count_bool_rep = np.zeros((2, len(expanded_keys)))
        kb_count = self._kb_manager.count_matches(self._curr_constraints)
        kb_size = self._kb_manager.get_kb_size()
        for key, value in kb_count.items():
            kb_count_abs_rep[expanded_keys.index(key)] = value / kb_size
            if value:
                kb_count_bool_rep[expanded_keys.index(key)] = 1

        return np.concatenate((
            curr_usr_inf_rep,
            curr_usr_req_rep,
            curr_agt_inf_rep,
            last_usr_act_rep,
            last_usr_act_inf_rep,
            last_usr_act_req_rep,
            last_agt_act_rep,
            last_agt_act_inf_rep,
            last_agt_act_req_rep,
            kb_count_abs_rep,
            kb_count_bool_rep
        ), axis=None)


    def get_state_dim(self):

        """
        Get the state dimension.

        Returns (int)
        -------------
        The dimension of the state.

        """

        return len(self.get_state())


    def _reset_agent_informs(self):

        """
        Reset the current agent informs.

        """

        self._curr_agt_inf = {}
        self._curr_constraints = self._curr_usr_inf.copy()


    def process_user_action(self, user_action):

        """
        Update the state tracker internal state given the user action.

        Parameters
        ----------
        user_action (dict or string)
            The user action.

        """

        # If the user rejects the current agent proposals or
        # informs about something that is in conflict with them,
        # reset them.
        if user_action == RJCT:
            self._reset_agent_informs()
        elif user_action not in USR_SPEC_ACTS:
            if get_conflict_keys(user_action[INF], self._curr_agt_inf):
                self._reset_agent_informs()
            # Update the state of the state tracker
            self._curr_usr_inf.update(user_action[INF])
            self._curr_constraints.update(user_action[INF])
            self._curr_usr_req.update(user_action[REQ])
        self._last_usr_act = user_action


    def process_agent_action(self, agent_action):

        """
        Process the agent action and update the state tracker internal state.

        Parameters
        ----------
        agent_action (tuple)
            The agent action.

        Returns (tuple or str)
        ----------------------
        The updated agent action.

        """

        if agent_action[0] == INF:
            # When the agent wants to inform the user about a specific key,
            # the state tracker finds a matching value for that key
            # to complete the action, given the state of the conversation.
            key = agent_action[1]
            self._curr_constraints.pop(key, None)
            value = self._kb_manager.find_matching_value(
                key,
                self._curr_constraints
            )
            # If there are no matching values, if the agent has proposed
            # something, then the agent proposals are withdrawn. Otherwise,
            # the agent informs the user that there are no matching values.
            if value == NMA:
                if self._curr_agt_inf:
                    self._reset_agent_informs()
                    agent_action = WCP
                else:
                    agent_action = NMA
            else:
                self._curr_agt_inf[key] = value
                self._curr_constraints[key] = value
                agent_action += (value,)
        self._last_agt_act = agent_action
        return agent_action
