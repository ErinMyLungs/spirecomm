import itertools
import sys
import time
import boto3
import numpy as np
from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass


if __name__ == "__main__":
    client = boto3.resource('s3')
    bucket = client.Bucket('1984withbunnies')

    solo = False
    control_group = False
    epochs=5

    train_class = PlayerClass.IRONCLAD
    seed_list = [
        "foobar", # problem seed
        "TKUZHLYGTK6B6",
        "MKMDE5BHDADPS",
        "5DWNQJBD5BPGM",
        "8O5SXDOKOJTT4",
        "JHHEA7KNEOGKI",
        "newbar", # problem seed
        "53HJXL2N4CEYI",
        "E4BMONWA67GME", #377dfjjkbolRH
        "LNYDX9VNZYATK",
    ]

    if solo:
        seed_list = [seed_list[0], seed_list[-4]]

    timestamp = str(int(time.time()))

    agent = SimpleAgent(
        chosen_class=train_class, use_default_drafter=control_group
    )


    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)


    current_weights = None
    high_score = 0.0
    for _ in range(epochs):
        timestamp = agent.update_timestamp()

        agent.reset_drafter(current_weights)
        agent.drafter.update_weights()

        agent.drafter.dump_weights(timestamp)
        possible_weights = f'weights_{timestamp}.npy'

        #upload weights
        bucket.upload_file(possible_weights, f'weights/weights_{timestamp}.npy')

        current_score = list()

        for seed in seed_list:
            result = coordinator.play_one_game(
                player_class=train_class, ascension_level=0, seed=seed
            )
            current_score.append(result)

        if control_group:
            filename = f'control_results_{timestamp}.csv'
        else:
            filename = f'game_results_{timestamp}.csv'

        bucket.upload_file(filename, f'runs/{filename}') #upload run stats
        if np.mean(current_score) >= high_score:
            current_weights = possible_weights
            high_score = np.mean(current_score)