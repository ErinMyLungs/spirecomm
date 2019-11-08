import itertools
import sys
import csv
import time
import boto3
import numpy as np
from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass
import os

if __name__ == "__main__":
    client = boto3.resource("s3")
    bucket = client.Bucket("1984withbunnies")

    solo = False
    control_group = False
    epochs = 10

    train_class = PlayerClass.IRONCLAD
    seed_list = [
        "foobar",  # problem seed
        "TKUZHLYGTK6B6",
        "MKMDE5BHDADPS",
        "5DWNQJBD5BPGM",
        "8O5SXDOKOJTT4",
        "JHHEA7KNEOGKI",
        "newbar",  # problem seed
        "53HJXL2N4CEYI",
        "E4BMONWA67GME",  # 377dfjjkbolRH
        "LNYDX9VNZYATK",
    ]

    if solo:
        seed_list = [seed_list[0], seed_list[-4]]

    timestamp = str(int(time.time()))

    agent = SimpleAgent(chosen_class=train_class, use_default_drafter=control_group)

    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)

    current_weights = None
    high_floor = 0.0
    high_score = 0.0
    weights_result_list = list()
    for _ in range(epochs):
        timestamp = agent.update_timestamp()

        agent.reset_drafter(current_weights)
        agent.drafter.update_weights()

        agent.drafter.dump_weights(timestamp)
        possible_weights = f"weights_{timestamp}.npy"

        # upload weights
        bucket.upload_file(possible_weights, f"weights/weights_{timestamp}.npy")

        current_score = list()
        current_floor = list()
        for seed in seed_list:
            score, floor = coordinator.play_one_game(
                player_class=train_class, ascension_level=0, seed=seed
            )
            current_score.append(score)
            current_floor.append(floor)

        if control_group:
            filename = f"control_results_{timestamp}.csv"
        else:
            filename = f"game_results_{timestamp}.csv"

        bucket.upload_file(filename, f"runs/{filename}")  # upload run stats
        if np.mean(current_floor) >= high_floor:
            current_weights = possible_weights
            high_floor = np.mean(current_floor)
            high_score = np.mean(current_score)
        elif np.mean(current_score) >= high_score:
            current_weights = possible_weights
            high_score = np.mean(current_score)
            high_floor = np.mean(current_floor)

        weights_result_list.append(
            {
                "timestamp": timestamp,
                "weight": possible_weights,
                "score": np.mean(current_score),
                "floor": np.mean(current_floor),
            }
        )
    mode = "a"
    if not os.path.exists(os.path.abspath("model_weight_results.csv")):
        mode = "w"

    with open("model_weight_results.csv", mode) as result_csv:
        writer = csv.DictWriter(result_csv, weights_result_list[0].keys())
        if mode == "w":
            writer.writeheader()
        writer.writerows(weights_result_list)
