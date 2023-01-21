import joblib
import os

from .StateTracker import StateTracker
from .RLAgent import RLAgent
from .RBAgent import RBAgent


class DialogueManager:

    """
    Dialogue manager.

    Attributes
    ----------
    _state_tracker (StateTracker) -> The state tracker.
    _rl_agt (RLAgent) -> The reinforcement learning agent.
    _rb_agt (RBAgent) -> The rule-based agent.
    _rl_mem (list of tuples) -> The RL memory.
    _warmup_mem (list of tuples) -> The warmup memory.
    warmup_mem_size (int) -> The warmup memory size.
    rl_mem_size (int) -> The RL memory size.

    Methods
    -------
    reset()
        Reset the dialogue manager.
    step(user_action, warmup)
        Perform a dialogue manager step given the user action.
    train()
        Train the RL agent.
    empty_rl_memory(fraction)
        Empty the RL memory.
    add_experience(state, action, reward, next_state, done, warmup)
        Add an experience to the memory.
    save(filepath, warmup)
        Save the dialogue manager.
    load(filepath, warmup)
        Load the dialogue manager.

    """

    def __init__(
        self,
        kb_filepath,
        rl_agent_args={},
        rl_mem_size=2**15,
        warmup_mem_size=2**12
    ):

        """
        Parameters
        ----------
        kb_filepath (str) -> The path to the knowledge base file.
        memory_size (int) -> The memory size.
        rl_agent_args (dict) -> The RL agent arguments.
        rl_mem_size (int) -> The RL memory size.
        warmup_mem_size (int) -> The warmup memory size.

        """

        self._state_tracker = StateTracker(kb_filepath)
        self._rl_agt = RLAgent(
            state_dim=self._state_tracker.get_state_dim(),
            **rl_agent_args
        )
        self._rb_agt = RBAgent()

        self._rl_mem = []
        self.rl_mem_size = rl_mem_size
        self._warmup_mem = []
        self.warmup_mem_size = warmup_mem_size


    def reset(self):

        """
        Reset the dialogue manager.

        """

        self._state_tracker.reset()
        self._rb_agt.reset()


    def step(self, user_action, warmup=False):

        """
        Perform a dialogue manager step given the user action.

        Parameters
        ----------
        user_action (str or dict) -> The user action.
        warmup (bool) -> Whether to use the rule-based agent or not.

        Returns
        -------
        state (numpy array) -> The state of the agent.
        index (int) -> The index of the action.
        action (tuple or str) -> The action.
        isrand (bool) -> Whether the action is random or not.

        """

        self._state_tracker.process_user_action(user_action)

        state = self._state_tracker.get_state()
        isrand = False
        if warmup:
            index, action = self._rb_agt.get_action(user_action)
        else:
            index, action, isrand = self._rl_agt.get_action(state)

        action = self._state_tracker.process_agent_action(action)
        if warmup:
            self._rb_agt.record_processed_action(action)

        return state, index, action, isrand


    def train(self):

        """
        Train the RL agent.

        """

        experience_set = self._warmup_mem + self._rl_mem
        self._rl_agt.train(experience_set)


    def empty_rl_mem(self, fraction=1):

        """
        Empty the memory.

        Parameters
        ----------
        fraction (float) -> The fraction of the RL memory to empty.

        """

        del self._rl_mem[:int(len(self._rl_mem) * fraction)]


    def add_experience(self, state, action, reward, next_state, done, warmup):

        """
        Add experience to the memory.

        Parameters
        ----------
        state : numpy array
            The state of the agent.
        action : int
            The index of the action.
        reward : float
            The reward.
        next_state : numpy array
            The next state of the agent.
        done : bool
            Whether the episode is done.
        warmup : bool
            Whether to add the experience to the warmup memory or not.

        Returns
        -------
        bool
            Whether the memory is already full or not.

        """

        if (
            len(self._warmup_mem) == self.warmup_mem_size and warmup
            or len(self._rl_mem) == self.rl_mem_size and not warmup
        ):
            return True
        if warmup:
            self._warmup_mem.append((state, action, reward, next_state, done))
        else:
            self._rl_mem.append((state, action, reward, next_state, done))
        return False


    def save(self, filepath):

        """
        Save the dialogue manager.
        
        Parameters
        ----------
        filepath : str
            The path to save the dialogue manager.

        """

        if not os.path.exists(filepath):
            os.mkdir(filepath)
        memory = {
            "warmup": self._warmup_mem,
            "rl": self._rl_mem
        }
        joblib.dump(memory, os.path.join(filepath, "memory"))
        self._rl_agt.save(os.path.join(filepath, "rl_agt"))


    def load(self, filepath):

        """
        Load the dialogue manager.
        
        Parameters
        ----------
        filepath : str
            The path to load the dialogue manager.

        """

        memory = joblib.load(os.path.join(filepath, "memory"))
        self._warmup_mem = memory["warmup"]
        self._rl_mem = memory["rl"]
        self._rl_agt.load(os.path.join(filepath, "rl_agt"))
