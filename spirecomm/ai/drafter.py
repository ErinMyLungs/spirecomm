#Drafting module to replace priorities.py for card choice
from spirecomm.ai.priorities import IroncladPriority
import random

class IroncladDraftModel():
    """
    A neural net drafter for The Ironclad class in Slay the Spire
    """
    def __init__(self):
        self.deck = {'Bash':1, 'Strike_r':5, 'Defends':4}
        self.floor = 0
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


    def update_floor(self, floor):
        if floor > self.floor:
            self.floor = floor

    def update_deck(self, card, remove=False):
        """
        Updates deck dictionary, incrementing count of cards up or down 1 and popping out any cards that are 0
        :param card: Card from card select
        :param remove: bool, if yes remove input card
        :return: None
        """
        if remove:
            card_count = self.deck.get(card)
            if card_count >1:
                self.deck['card'] -=1
            else:
                self.deck.pop('card')
            return

        if self.deck.get(card):
            self.deck[card] += 1
            return
        else:
            self.deck[card] = 1