import random

from .config import (
    USR_INF_NUM_KEYS, USR_INF_STR_KEYS, USR_INF_ENUM_KEYS, USR_REQ_KEYS,
    USR_SPEC_ACTS, INF, REQ
)


class ErrorModelController:

    """
    Error Model Controller.

    Parameters
    ----------
    error_probability : float
        The probability of infusing error.

    Methods
    -------
    infuse_error(user_action)
        Infuse errors into the user action.
    _pop_request_key(key, user_action)
        Remove a key from the user action requests.
    _pop_inform_key(key, user_action)
        Remove a key from the user action informs.
    _switch_inf_key_to_req_key(key, user_action)
        Switch a key from the user action informs to requests.
    _corrupt_inf_enum_value(key, user_action)
        Switch a value from the user action informs to another value.
    _corrupt_inf_key(key, user_action)
        Switch a key from the user action informs to another inform key.
    _corrupt_req_key(key, user_action)
        Switch a key from the user action requests to another request key.
    _corrupt_spec_act(user_action)
        Switch the user action to a different special action.
    _switch_spec_act_to_inf(user_action)
        Switch the user action to an inform.
    _switch_spec_act_to_req(user_action)
        Switch the user action to a request.
    
    """

    def __init__(self, error_probability=0):

        """
        Parameters
        ----------
        error_probability : float
            The probability of infusing error.

        """

        self.error_probability = error_probability


    def _pop_request_key(self, key, user_action):

        """
        Remove a key from the user action requests.

        Parameters
        ----------
        key : string
            The key to be removed.
        user_action : dict
            The user action.

        """

        user_action[REQ].remove(key)


    def _pop_inform_key(self, key, user_action):

        """
        Remove a key from the user action informs.

        Parameters
        ----------
        key : string
            The key to be removed.
        user_action : dict
            The user action.

        """

        user_action[INF].pop(key)


    def _switch_inf_key_to_req_key(self, key, user_action):

        """
        Switch a key from the user action informs to requests.

        Parameters
        ----------
        key : string
            The key to be switched.
        user_action : dict
            The user action.

        """

        user_action[INF].pop(key)
        user_action[REQ].append(key)


    def _corrupt_inf_enum_value(self, key, user_action):

        """
        Switch a value from the user action informs to another value.

        Parameters
        ----------
        key : string
            The key to be switched.
        user_action : dict
            The user action.

        """

        candidate_set = USR_INF_ENUM_KEYS[key]
        user_action[INF][key] = random.choice(
            [v for v in candidate_set if v != user_action[INF][key]]
        )


    def _corrupt_inf_key(self, key, user_action):

        """
        Switch a key from the user action informs to another inform key.

        Parameters
        ----------
        key : string
            The key to be switched.
        user_action : dict
            The user action.

        """
        
        candidate_set = (
            USR_INF_STR_KEYS if key in USR_INF_STR_KEYS
            else USR_INF_NUM_KEYS
        )
        sub_key = random.choice(
            [k for k in candidate_set if k not in user_action[INF]]
        )
        user_action[INF][sub_key] = user_action[INF].pop(key)


    def _corrupt_req_key(self, key, user_action):
    
        """
        Switch a key from the user action requests to another request key.

        Parameters
        ----------
        key : string
            The key to be switched.
        user_action : dict
            The user action.

        """

        sub_key = random.choice(
            [k for k in USR_REQ_KEYS if k not in user_action[REQ]]
        )
        user_action[REQ].append(sub_key)
        user_action[REQ].remove(key)


    def _corrupt_spec_act(self, user_action):

        """
        Switch the user action to a different special action.

        Parameters
        ----------
        user_action : dict
            The user action.

        Returns
        -------
        dict
            The new user action.

        """

        return random.choice(
            [sa for sa in USR_SPEC_ACTS if sa != user_action]
        )


    def _switch_spec_act_to_inf(self, user_action):

        """
        Switch the user action to an inform.

        Parameters
        ----------
        user_action : dict
            The user action.

        Returns
        -------
        dict
            The new user action.

        """

        return {
            INF: {random.choice(USR_INF_STR_KEYS): user_action},
            REQ: []
        }


    def _switch_spec_act_to_req(self, user_action):
            
        """
        Switch the user action to a request.

        Parameters
        ----------
        user_action : dict
            The user action.

        Returns
        -------
        dict
            The new user action.

        """

        return {
            INF: {},
            REQ: [random.choice(USR_REQ_KEYS)]
        }


    def infuse_error(self, user_action):

        """
        Infuse errors into the user action.

        Parameters
        ----------
        user_action : dict or string
            The user action.

        Returns
        -------
        user_action (string or dict)
            The user action
        error_infused (bool)
            Whether an error has been infused or not.

        """

        error_infused = False
        if random.random() < self.error_probability:
            if user_action in USR_SPEC_ACTS:
                error_functions = random.choice([
                    self._switch_spec_act_to_req,
                    self._switch_spec_act_to_inf,
                    self._corrupt_spec_act
                ])
                user_action = error_functions(user_action)
            else:
                key = random.choice(user_action[REQ] + list(user_action[INF]))
                if key in user_action[INF]:
                    error_functions = [self._pop_inform_key]
                    if key in USR_INF_ENUM_KEYS:
                        error_functions.append(self._corrupt_inf_enum_value)
                    else:
                        error_functions.append(self._corrupt_inf_key)
                    if key in USR_REQ_KEYS:
                        error_functions.append(self._switch_inf_key_to_req_key)
                    random.choice(error_functions)(key, user_action)
                else:
                    random.choice([
                        self._corrupt_req_key,
                        self._pop_request_key
                    ])(key, user_action)
            error_infused = True

        return user_action, error_infused
