from keras.models import Sequential, clone_model, load_model
from keras.optimizers import Adam
from keras.layers import Dense
from keras import Input
from tqdm import tqdm
import numpy as np
import random

from .config import AGT_ACTS


class RLAgent:

    """
    Reinforcement learning agent.

    Attributes
    ----------
    gamma : float
        The discount factor.
    epsilon : float
        The probability of taking a random action.
    epsilon_decay : float
        The decay rate of epsilon.
    vanilla : bool
        Whether to use vanilla DQN or Double DQN.
    batch_size : int
        The batch size for training.
    _beh_model : keras model
        The behavior model. It is used to predict the Q-values.

    Methods
    -------
    _build_qnet(
        n_hidden,
        hidden_activation,
        n_output,
        output_activation,
        loss,
        optimizer
    )
        Build the Q-network.
    get_action(state)
        Get the action.
    train(experience_set)
        Train the agent.
    save(filepath)
        Save the agent.
    load(filepath)
        Load the agent.

    """

    def __init__(
        self,
        state_dim,
        qnet_n_hidden=100,
        qnet_hidden_activation="relu",
        qnet_output_activation="linear",
        qnet_loss="MSE",
        qnet_optimizer=Adam(learning_rate=5e-4),
        gamma=0.9,
        init_epsilon=0.,
        epsilon_decay=0.99,
        vanilla=True,
        batch_size=256,
    ):

        """
        Parameters
        ----------
        state_dim: int
            The dimension of the state.
        qnet_n_hidden : int
            The number of hidden units in the Q-network.
        qnet_hidden_activation : str
            The activation function of the hidden units in the Q-network.
        qnet_output_activation : str
            The activation function of the output units in the Q-network.
        qnet_loss : str
            The loss function of the Q-network.
        qnet_optimizer : keras optimizer
            The optimizer of the Q-network.
        gamma : float
            The discount factor.
        init_epsilon : float
            The probability of taking a random action.
        epsilon_decay : float
            The decay rate of epsilon.
        vanilla : bool
            Whether to use vanilla DQN or Double DQN.
        batch_size : int
            The batch size for training.

        """

        self.gamma = gamma
        self.epsilon = init_epsilon
        self.epsilon_decay = epsilon_decay
        self.vanilla = vanilla
        self.batch_size = batch_size

        self._build_qnet(
            state_dim=state_dim,
            n_hidden=qnet_n_hidden,
            hidden_activation=qnet_hidden_activation,
            n_output=len(AGT_ACTS),
            output_activation=qnet_output_activation,
            loss=qnet_loss,
            optimizer=qnet_optimizer
        )


    def _build_qnet(
        self,
        state_dim,
        n_hidden,
        hidden_activation,
        n_output,
        output_activation,
        loss,
        optimizer
    ):

        """
        Build the Q-network.

        Parameters
        ----------
        state_dim: int
            The dimension of the state.
        n_hidden : int
            The number of hidden units in the Q-network.
        hidden_activation : str
            The activation function of the hidden units in the Q-network.
        n_output : int
            The number of output units in the Q-network.
        output_activation : str
            The activation function of the output units in the Q-network.
        loss : str
            The loss function of the Q-network.
        optimizer : keras optimizer
            The optimizer of the Q-network.

        """

        self._beh_model = Sequential([
            Input(shape=(state_dim,)),
            Dense(n_hidden, activation=hidden_activation),
            Dense(n_output, activation=output_activation)
        ])
        self._beh_model.compile(loss=loss, optimizer=optimizer)


    def get_action(self, state):

        """
        Get the action.

        Parameters
        ----------
        state : numpy array
            The state of the agent.
        
        Returns
        -------
        index : int
            The index of the action.
        action : tuple
            The action.
        isrand : bool
            Whether the action is random or not.

        """

        isrand = False
        if self.epsilon > random.random():
            action = random.choice(AGT_ACTS)
            isrand = True
        else:
            state = np.expand_dims(state, axis=0)
            q = self._beh_model.predict(state, verbose=False)
            action = AGT_ACTS[np.argmax(q.flatten())]
        index = AGT_ACTS.index(action)
        return index, action, isrand


    def train(self, experience_set):

        """
        Train the agent.

        Parameters
        ----------
        experience_set : list of tuples
            The set of experiences.
            Experiences are (state, action, reward, next_state, done) tuples.

        """

        # Clone the behavior model to the target model
        tar_model = clone_model(self._beh_model)
        tar_model.set_weights(self._beh_model.get_weights())

        # Prepare batch of experiences from the memory (experience replay)
        random.shuffle(experience_set)
        batches = [
            experience_set[i : i + self.batch_size]
            for i in range(0, len(experience_set), self.batch_size)
        ]

        # Train the agent
        for batch in tqdm(batches):
            s = np.array([sarsd[0] for sarsd in batch]) # States
            s_prime = np.array([sarsd[3] for sarsd in batch]) # Next states
            q = self._beh_model.predict(s, verbose=False) # Action values
            tar_q_prime = tar_model.predict(s_prime, verbose=False)
            if not self.vanilla:
                beh_q_prime = self._beh_model.predict(s_prime, verbose=False)
            # Q-Learning
            for i, (_, a, r, _, d) in enumerate(batch):
                v_prime = (
                    np.amax(tar_q_prime[i]) if self.vanilla
                    else tar_q_prime[i][np.argmax(beh_q_prime[i])]
                ) # Value of s'
                v_prime *= not d
                q[i][a] = r + self.gamma * v_prime
            self._beh_model.fit(s, q, epochs=1, verbose=False)

        self.epsilon *= self.epsilon_decay


    def save(self, filepath):

        """
        Save the behavioural model of the agent.

        Parameters
        ----------
        filepath : str
            The path to save the agent.

        """

        self._beh_model.save(filepath)


    def load(self, filepath):

        """
        Load the behavioural model of the agent.
        
        Parameters
        ----------
        filepath : str
            The path to load the agent.
        
        """

        self._beh_model = load_model(filepath)
