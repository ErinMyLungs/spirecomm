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
import pandas as pd
import ast

if __name__ == "__main__":
    client = boto3.resource("s3")
    bucket = client.Bucket("1984withbunnies")

    solo = True
    control_group = False
    epochs = 1

    train_class = PlayerClass.IRONCLAD
    seed_list = [
        "foobar",  # problem seed
        "TKUZHLYGTK6B6",
        "MKMDE5BHDADPS", #9 something
        "5DWNQJBD5BPGM",
        "8O5SXDOKOJTT4",
        "JHHEA7KNEOGKI",
        "newbar",  # problem seed
        "53HJXL2N4CEYI",
        "E4BMONWA67GME",  # 377dfjjkbolRH
        "LNYDX9VNZYATK",
    ]

    if solo:
        seed_list = [seed_list[-1]]

    timestamp = str(int(time.time()))

    agent = SimpleAgent(chosen_class=train_class, use_default_drafter=control_group)

    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)

    if not os.path.exists(os.path.abspath('model_weight_results.csv')):
        current_weights = None
        high_floor = 0.0
        high_score = 0.0
    else:
        all_results = pd.read_csv('model_weight_results.csv').tail(10)
        _, current_weights, high_score, high_floor = all_results.loc[all_results.floor == all_results.floor.max()].values[0]

    weights_result_list = list()

    for ep in range(epochs):
        if ep != 0:
            last_results = pd.read_csv(f'game_results_{timestamp}.csv')
            card_choice_set = set()
            for choice_dict in last_results.choices:
                choice_list = list(ast.literal_eval(choice_dict).values())
                for cl in choice_list:
                    for card, _ in cl:
                        card_choice_set.add(agent.drafter.card_index_dict['cards'].get(card))

        timestamp = agent.update_timestamp()

        agent.reset_drafter(current_weights)

        if ep != 0:
            # lr = 5 * ((epochs-ep)/epochs)
            agent.drafter.update_weights_by_cards(card_choice_set, learning_rate=5)
        else:
            agent.drafter.update_weights(n_updates=400, learning_rate=5)
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
            agent.reset_drafter(current_weights)
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
        if not control_group and ep%5 == 0:
            # write results every 5 epochs so if having to abort a long run early, progress isn't lost
            mode = "a"
            if not os.path.exists(os.path.abspath("model_weight_results.csv")):
                mode = "w"

            with open("model_weight_results.csv", mode) as result_csv:
                writer = csv.DictWriter(result_csv, weights_result_list[0].keys())
                if mode == "w":
                    writer.writeheader()
                writer.writerows(weights_result_list)

            weights_result_list = list()