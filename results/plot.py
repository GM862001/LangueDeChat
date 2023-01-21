import matplotlib.pyplot as plt
import json

with open("results/warmup_results.json") as warmup_results_file:
    warmup_results = json.load(warmup_results_file)
with open("results/train_results.json") as train_results_file:
    train_results = json.load(train_results_file)

warmup_avg_reward = warmup_results["avg_reward"]
warmup_avg_success = warmup_results["avg_success"]
train_avg_rewards = train_results["avg_rewards"]
train_avg_successes = train_results["avg_successes"]

average_window = 10
train_avg_rewards = [
    sum(train_avg_rewards[max(0, i - average_window) : i]) / min(average_window, i)
    for i in range(1, len(train_avg_rewards) + 1)
]
train_avg_successes = [
    sum(train_avg_successes[max(0, i - average_window) : i]) / min(average_window, i)
    for i in range(1, len(train_avg_successes) + 1)
]

plt.figure(figsize=(10, 5))
plt.plot(train_avg_rewards, label=f"Train average reward (average window = {average_window}))")
plt.axhline(y=warmup_avg_reward, color='orange', linestyle='--', label="Warmup average reward")
plt.xlabel("Epoch")
plt.ylabel("Reward")
plt.legend()
plt.savefig('results/avg_rewards.png')

plt.figure(figsize=(10, 5))
plt.plot(train_avg_successes, label=f"Train average success (average window = {average_window})")
plt.axhline(y=warmup_avg_success, color='orange', linestyle='--', label="Warmup average success")
plt.xlabel("Epoch")
plt.ylabel("Success rate")
plt.legend()
plt.savefig('results/avg_successes.png')
