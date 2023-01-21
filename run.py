# ======================================================================
#                               run.py  
# ----------------------------------------------------------------------
#      This file contains some routines to simulate the conversation
#                  between the agent and the user.
# ----------------------------------------------------------------------

import logging


def run_episode(
    DM, # Dialogue Manager
    US, # User Simulator
    EMC, # Error Model Controller 
    warmup # Whether the episode is a warmup episode
):

    episode_reward = 0
    done = False
    DM.reset()
    US.reset()
    init_usr_act = US.get_init_action()
    state, agt_act_idx, agt_act, isrand = DM.step(
        init_usr_act,
        warmup=warmup
    )
    logging.info(
        f"USERSIM GOAL -> {US._goal}\n"
        f"USERSIM INIT ACTION -> {init_usr_act}"
    )

    while not done:
        logging.info(
            f"AGENT ACTION {'(RANDOM)' if isrand else ''} -> {agt_act}"
        )
        usr_act, reward, done, success = US.step(agt_act)
        if not done:
            logging.info(f"USERSIM ACTION -> {usr_act}")
            usr_act, error_infused = EMC.infuse_error(usr_act)
            if error_infused:
                logging.info(
                    f"CORRUPTED USERSIM ACTION -> {usr_act}"
                )
        logging.info(
            f"USERSIM STATUS -> "
            f"Not yet answered requests: {US._not_answ_req}, "
            f"Not yet expressed constraints: {US._not_sent_inf}"
        )
        next_state, next_agt_act_idx, next_agt_act, isrand = DM.step(
            usr_act,
            warmup=warmup
        )
        is_memory_full = DM.add_experience(
            state,
            agt_act_idx,
            reward,
            next_state,
            done,
            warmup
        )

        state = next_state
        agt_act_idx = next_agt_act_idx
        agt_act = next_agt_act
        episode_reward += reward

    return episode_reward, success, is_memory_full


def run_period(
    DM, # Dialogue Manager
    US, # User Simulator
    EMC, # Error Model Controller
    warmup, # Whether the period is a warmup period
    max_episodes=None # Maximum number of episodes
):

    period_reward = 0
    period_success = 0
    n_episode = 0
    is_memory_full = False
    while not is_memory_full and (warmup or n_episode < max_episodes):
        n_episode += 1
        logging.info(f"***** EPISODE N. {n_episode} *****")
        reward, success, is_memory_full = run_episode(DM, US, EMC, warmup)
        logging.info(
            f"EPSIODE N. {n_episode} COMPLETED: "
            f"success = {success}, reward = {reward}"
        )
        logging.info(f"------------------------------------")
        period_reward += reward
        period_success += success

    avg_success = period_success / n_episode
    avg_reward = period_reward / n_episode

    return avg_success, avg_reward, is_memory_full
