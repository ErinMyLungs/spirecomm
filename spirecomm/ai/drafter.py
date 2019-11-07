#Drafting module to replace priorities.py for card choice
from spirecomm.ai.priorities import IroncladPriority
import random

class IroncladDraftModel():
    """
    A neural net drafter for The Ironclad class in Slay the Spire
    """
    def choose_card(self, potential_choices):
        """
        Takes in potential card choices as list and returns a card to select
        :param potential_choices: list of cards to select
        :return: single card to select
        """
        if len(potential_choices) <= 0:
            return(0)
        else:
            return random.choice(potential_choices)