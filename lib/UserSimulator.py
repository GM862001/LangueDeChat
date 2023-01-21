import random
import json

from .KBManager import KBManager
from .config import (
    USR_REQ_KEYS, USR_SPEC_ACTS, GOAL_KEY, OWT,
    USRSIM_REQ_ONLY_AFTER_AGT_INF, USRSIM_INIT_INF,
    THX, RJCT, INF, REQ, NMA, WCP
)
from .match import get_conflict_keys, CONSTRAINED_KEYS_MAPS


class UserSimulator:

    """
    User simulator.

    Parameters
    ----------
    _goals : list
        The list of user goals.
    patience : int
        Patience of the user simulator (maximum number of rounds of the conversation).
    _kb_manager: KBManager
        The knowledge base manager.
    _goal: dict
        The goal of the user simulator.
    _action: dict or str
        The current action of the user simulator.
    _curr_agt_inf: dict
        The proposals made by the agent.
    _already_matched_inf: set
        Constraints that doesn't need to be expressed because they are already satisfied by the agent proposal.
    _not_sent_inf: set
        Constraints that have not yet been expressed by the user simulator.
    _not_answ_req: set
        Requests that have not yet been answered by the agent.
    _round: int
        Current round of the conversation.
    _satisfied: bool
        Whether the user simulator is satisfied or not.

    Methods
    -------
    reset()
        Reset the user simulator.
    _filter_req_keys(keys_to_filter)
        Filter the keys that can be requested at the current state of the conversation.
    _reset_agent_informs()
        Reset the current agent informs.
    _pick_random_action()
        Pick a random action.
    _response_to_inform(agent_action)
        Update the user simulator action and state when the agent informs something.
    _response_to_request(agent_action)
        Update the user simulator action and state when the agent requests something.
    get_init_action()
        Get the initial action of the user simulator.
    step(agent_action)
        Perform a step of the conversation.

    """

    def __init__(self, goals_filepath, kb_filepath, patience=15):

        """
        Parameters
        ----------
        goals_filepath : str
            Path to the JSON file containing the user goals.
        kb_filepath : str
            Path to the JSON file containing the knowledge base.
        patience : int
            Maximum number of rounds of the conversation (patience of the user simulator).

        """

        with open(goals_filepath) as goals_file:
            self._goals = json.load(goals_file)

        # A KBManager is needed to check a posteriori if the agent proposal is actually accettable or not.
        # This is done to simulate the actual retrieving of the proposed goal
        # by the user after the end of the conversation.
        self._kb_manager = KBManager(kb_filepath)

        self.patience = patience
        self.reset()


    def reset(self):

        """
        Reset the user simulator.

        """

        # Internal state variables
        self._goal = random.choice(self._goals)
        self._curr_agt_inf = {}
        self._already_matched_inf = set()
        self._not_sent_inf = set(self._goal[INF])
        self._not_answ_req = set(self._goal[REQ] + [GOAL_KEY])
        self._satisfied = False
        self._round = 0


    def _filter_req_keys(self, keys):

        """
        Filter the keys that can be requested at the current state of the conversation.

        Parameters
        ----------
        keys : list
            The keys to filter.

        Returns
        -------
        list
            The filtered keys.

        """

        if self._curr_agt_inf:
            return keys
        else:
            return [k for k in keys if k not in USRSIM_REQ_ONLY_AFTER_AGT_INF]


    def _reset_agent_informs(self):

        """
        Reset the current agent informs.

        """

        self._curr_agt_inf = {}
        # The same requests will be made again for the next agent proposal.
        self._not_answ_req = set(self._goal[REQ] + [GOAL_KEY])
        # The next agent proposal will need to be checked against the
        # constraints that were satisfied by the previous one.
        self._not_sent_inf.update(self._already_matched_inf)
        self._already_matched_inf = set()


    def _pick_random_action(self):

        """
        Pick a random action.

        """

        # Pick a random action among the following:
        # 1) If the agent has not yet expressed all its constraints,
        # then extract one randomly and choose a random action among the following:
        #     1.a) If the key is a user requestable key, request it,
        #     waiting for the agent to inform about its value so that to check it;
        #     1.b) Else inform the agent about the constraint;
        # 2) Else if it has not been informed about all its needed information,
        # then extract one randomly and request it;
        # 3) Thanks the agent.
        requestable_keys = self._filter_req_keys(
            list(self._not_answ_req)
        )
        if self._not_sent_inf and random.random() < 2 / 3:  # 1)
            key = random.choice(list(self._not_sent_inf))
            if (
                key in self._filter_req_keys(USR_REQ_KEYS)
                and random.random() < 1 / 2
            ):  # 1.a)
                self._action[REQ].append(key)
            else:  # 1.b)
                self._action[INF][key] = self._goal[INF][key]
        elif requestable_keys and random.random() < 2 / 3:  # 2)
            self._action[REQ].append(random.choice(requestable_keys))
        else:  # 3)
            self._action = THX


    def _response_to_inform(self, agent_action):

        """
        Update the user simulator action and state when the agent informs something.

        Parameters
        ----------
        agent_action : tuple
            The agent action.

        """

        _, inf_key, inf_value = agent_action
        inf_dict = {inf_key: inf_value}
        conflict_keys = get_conflict_keys(inf_dict, self._goal[INF])
        if conflict_keys:
            self._reset_agent_informs()
            self._not_sent_inf.update(conflict_keys) # We will need to inform the agent again about these keys.
            key = random.choice(list(conflict_keys))
            if random.random() < 1 / 2:
                self._action[INF][key] = self._goal[INF][key]
            else:
                self._action = RJCT
        else:
            if (
                inf_key in self._curr_agt_inf
                and self._curr_agt_inf[inf_key] != inf_value
            ):
                self._reset_agent_informs()
            constraining_keys = [
                ck for ck, _ in CONSTRAINED_KEYS_MAPS[inf_key]
                if ck in self._goal[INF]
            ] if inf_key in CONSTRAINED_KEYS_MAPS else []
            self._already_matched_inf.update(constraining_keys)
            self._not_sent_inf.difference_update(constraining_keys)
            if inf_key in self._goal[INF] and inf_key in self._not_sent_inf:
                self._already_matched_inf.add(inf_key)
            self._not_sent_inf.discard(inf_key)
            self._not_answ_req.discard(inf_key)
            self._curr_agt_inf[inf_key] = inf_value
            self._satisfied = not (self._not_answ_req | self._not_sent_inf)
            self._pick_random_action()


    def _response_to_request(self, agent_action):

        """
        Update the user simulator action and state when the agent requests something.

        Parameters
        ----------
        agent_action : tuple
            The request of the agent.

        """

        _, req_key = agent_action

        # 1) If the agent requests a constraint of the user simulator,
        # inform the agent about the constraint;
        # 2) Else if the agent requests for a key which is constrained
        # by some constraints of the user simultor,
        # inform the agent about those constraints;
        # 3) Else if the agent requests for a key that the user simulator wants to know,
        # choose a random action among the following ones:
        #   3.a) If the user simulator has already proposed a value for that key,
        #   then inform the agent about that value;
        #   3.b) Else if the user simulator can request that key, request it;
        #   3.c) Else inform the agent that any value is accettable for that key;
        # 4) Else inform the agent that any value is accettable for that key. Additionally,
        # with some probability, inform the agent about a not yet expressed constraint, if any.
        active_constraining_keys = [
            ck for ck, _ in CONSTRAINED_KEYS_MAPS[req_key]
            if ck in self._goal[INF]
        ] if req_key in CONSTRAINED_KEYS_MAPS else []
        if req_key in self._goal[INF]:  # 1)
            self._action[INF][req_key] = self._goal[INF][req_key]
        elif active_constraining_keys:  # 2)
            for ack in active_constraining_keys:
                self._action[INF][ack] = self._goal[INF][ack]
        elif req_key in self._goal[REQ]:  # 3)
            if req_key in self._curr_agt_inf and random.random() < 1 / 3:  # 3.a)
                self._action[INF][req_key] = self._curr_agt_inf[req_key]
            elif (
                req_key in self._filter_req_keys(self._goal[REQ])
                and random.random() < 1 / 2
            ): # 3.b)
                self._action[REQ].append(req_key)
            else:  # 3.c)
                self._action[INF][req_key] = OWT
        else:  # 4)
            self._action[INF][req_key] = OWT
            if self._not_sent_inf and random.random() < 1 / 3:
                key = random.choice(list(self._not_sent_inf))
                self._action[INF][key] = self._goal[INF][key]


    def get_init_action(self):

        """
        Get the initial action of the user simulator.

        Returns
        -------
        action (dict)
            The initial action of the user simulator.

        """

        action = {
            INF: {},
            REQ: []
        }

        # For every compulsory initial inform,
        # if it is present in the user goal, inform it.
        for key in USRSIM_INIT_INF:
            if key in self._goal[INF]:
                action[INF][key] = self._goal[INF][key]

        # If no compulsory initial inform was present in the user goal,
        # then choose a random one to inform.
        if not action[INF]:
            key, value = random.choice(list(self._goal[INF].items()))
            action[INF][key] = value

        # Update the state of the user simulator given its action
        for key in action[INF]:
            self._not_sent_inf.discard(key)

        # Additionally, request something, if anything to request.
        requestable_keys = self._filter_req_keys(self._goal[REQ])
        if requestable_keys:
            action[REQ].append(random.choice(requestable_keys))

        return action


    def step(self, agent_action):

        """
        Perform a step of the conversation.

        Parameters
        ----------
        agent_action : tuple or str
            The action of the agent.

        """

        self._round += 1
        self._action = {
            INF: {},
            REQ: []
        }
        if agent_action == WCP:
            self._reset_agent_informs()
            self._pick_random_action()
        elif agent_action[0] == INF:
            self._response_to_inform(agent_action)
        elif agent_action[0] == REQ:
            self._response_to_request(agent_action)
        if agent_action == NMA:
            done = True
            self._satisfied = False
        else:
            done = self._round == self.patience or self._satisfied
            self._satisfied = (
                self._satisfied
                and self._kb_manager.check_goal_proposal_consistency(
                    self._curr_agt_inf[GOAL_KEY],
                    self._goal[INF]
                )
                and self._kb_manager.check_goal_proposal_consistency(
                    self._curr_agt_inf[GOAL_KEY],
                    self._curr_agt_inf
                )
            )  # The goal proposal is checked a posteriori, after done has been set

        # Update the state of the user simulator given its action
        if not done and self._action not in USR_SPEC_ACTS:
            for key in self._action[INF]:
                self._not_sent_inf.discard(key)

        # Compute the reward
        if not done:
            reward = -1
        elif self._satisfied:
            goal_complexity = len(self._goal[REQ]) + len(self._goal[INF])
            reward = (2 * self.patience + goal_complexity)
        else:
            n_not_answ_reqs = len(self._not_answ_req)
            not_answered_ratio = n_not_answ_reqs / (len(self._goal[REQ]) + 1) # +1 takes into account the goal key
            n_not_sent_infs = len(self._not_sent_inf)
            not_informed_ratio = n_not_sent_infs / len(self._goal[INF])
            weight = not_answered_ratio + not_informed_ratio
            reward = - round(weight * self.patience)

        return self._action, reward, done, self._satisfied
