import logging
import json

from lib import UserSimulator
from lib import ErrorModelController
from lib import DialogueManager
from run import run_period

logging.basicConfig(
    filename="log/warmup.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(message)s"
)


if __name__ == "__main__":

    dialogue_manager = DialogueManager(kb_filepath="data/knowledge_base.json")
    usersim = UserSimulator(
        kb_filepath="data/knowledge_base.json",
        goals_filepath="data/user_goals.json"
    )
    error_model_controller = ErrorModelController(error_probability=0.02)

    logging.info(
        "************************************************\n"
        "**************** WARMUP STARTED ****************\n"
        "************************************************\n"
    )

    avg_success, avg_reward, _ = run_period(
        dialogue_manager,
        usersim,
        error_model_controller,
        warmup=True
    )

    logging.info(
        "\n==================================\n"
        "         WARMUP COMPLETED         \n"
        "----------------------------------\n"
        f"Average success = {avg_success}\n"
        f"Average reward = {avg_reward}\n"
        "==================================\n"
    )
    
    warmup_results = {
        "avg_success": avg_success,
        "avg_reward": avg_reward
    }
    with open("results/warmup_results.json", "w") as warmup_results_file:
        warmup_results_file.write(json.dumps(warmup_results))
    dialogue_manager.save("models/WarmedUp")

