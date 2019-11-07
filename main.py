import itertools
import datetime
import sys
import time

from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass


if __name__ == "__main__":
    train_class = PlayerClass.IRONCLAD
    seed = '3BLZA4F5DPM6P'
    agent = SimpleAgent(chosen_class=train_class, use_default_drafter=True)
    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)

    start = time.time()
    result = coordinator.play_one_game(player_class=train_class, ascension_level=0, seed=seed)
    end = time.time() - start
    with open('test_writing_314159.txt', 'w') as file:
        file.write(str(end))
    print(end)