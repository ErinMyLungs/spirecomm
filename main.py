import itertools
import sys
import time
import boto3

from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass


if __name__ == "__main__":
    client = boto3.resource('s3')
    bucket = client.Bucket('1984withbunnies')
    solo = True
    control_group = False

    train_class = PlayerClass.IRONCLAD
    seed_list = [
        "foobar", # problem seed
        "TKUZHLYGTK6B6",
        "MKMDE5BHDADPS",
        "5DWNQJBD5BPGM",
        "8O5SXDOKOJTT4",
        "JHHEA7KNEOGKI",
        "new_bar", # problem seed
        "53HJXL2N4CEYI",
        "E4BMONWA67GME", #377dfjjkbolRH
        "LNYDX9VNZYATK",
    ]

    if solo:
        seed_list = [seed_list[0], seed_list[-4]]

    timestamp = str(int(time.time()))

    agent = SimpleAgent(
        chosen_class=train_class, use_default_drafter=control_group, timestamp=timestamp
    )

    # agent.drafter.dump_weights(timestamp)
    # bucket.upload_file(f'weights_{timestamp}.npy', f'weights/weights_{timestamp}.npy')
    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)

    for seed in seed_list:
        result = coordinator.play_one_game(
            player_class=train_class, ascension_level=0, seed=seed
        )
        print(result)
        time.sleep(10)
    if control_group:
        filename = f'control_results_{timestamp}.csv'
    else:
        filename = f'game_results_{timestamp}.csv'
    bucket.upload_file(filename, f'runs/{filename}')
