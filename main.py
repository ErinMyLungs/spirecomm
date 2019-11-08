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
    solo = False
    control_group = False

    train_class = PlayerClass.IRONCLAD
    seed_list = [
        "3BLZA4F5DPM6P",
        "TKUZHLYGTK6B6",
        "MKMDE5BHDADPS",
        "5DWNQJBD5BPGM",
        "8O5SXDOKOJTT4",
        "JHHEA7KNEOGKI",
        "LI7X71KSALAGR",
        "53HJXL2N4CEYI",
        "E4BMONWA67GME",
        "LNYDX9VNZYATK",
    ]

    if solo:
        seed_list = seed_list[:3]

    timestamp = str(int(time.time()))

    agent = SimpleAgent(
        chosen_class=train_class, use_default_drafter=control_group, timestamp=timestamp, bucket=bucket
    )

    agent.drafter.dump_weights(timestamp)
    bucket.upload(f'weights_{timestamp}.npy', f'weights/weights_{timestamp}.npy')
    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)

    for seed in seed_list:
        result = coordinator.play_one_game(
            player_class=train_class, ascension_level=0, seed=seed
        )

    if control_group:
        filename = f'control_results_{timestamp}.csv'
    else:
        filename = f'game_results_{timestamp}.csv'
    bucket.upload(filename, f'runs/{filename}')
