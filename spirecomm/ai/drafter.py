# Drafting module to replace priorities.py for card choice
from spirecomm.ai.priorities import IroncladPriority
import random
import numpy as np
import os
import time


class IroncladDraftModel:
    """
    A neural net drafter for The Ironclad class in Slay the Spire
    """

    def __init__(self, weights: str = None):
        self.deck = {"BASH": 1, "STRIKE_R": 5, "DEFEND_R": 4}
        self.floor = 0
        self.deck_pick = {}

        self.card_index_dict = {
            "cards": {
                "HEADBUTT": 0,
                "BRUTALITY": 1,
                "BLUDGEON": 2,
                "LIMIT BREAK": 3,
                "EXHUME": 4,
                "DOUBLE TAP": 5,
                "TRUE GRIT": 6,
                "BODY SLAM": 7,
                "FEEL NO PAIN": 8,
                "SEVER SOUL": 9,
                "WILD STRIKE": 10,
                "STRIKE_R": 11,
                "BURNING PACT": 12,
                "ENTRENCH": 13,
                "INTIMIDATE": 14,
                "DROPKICK": 15,
                "PERFECTED STRIKE": 16,
                "BERSERK": 17,
                "INFERNAL BLADE": 18,
                "WARCRY": 19,
                "FEED": 20,
                "RECKLESS CHARGE": 21,
                "SEEING RED": 22,
                "POWER THROUGH": 23,
                "REAPER": 24,
                "DEFEND_R": 25,
                "HAVOC": 26,
                "DUAL WIELD": 27,
                "EVOLVE": 28,
                "FLAME BARRIER": 29,
                "OFFERING": 30,
                "SHOCKWAVE": 31,
                "FLEX": 32,
                "BASH": 33,
                "INFLAME": 34,
                "SWORD BOOMERANG": 35,
                "IRON WAVE": 36,
                "THUNDERCLAP": 37,
                "DISARM": 38,
                "DARK EMBRACE": 39,
                "COMBUST": 40,
                "CLOTHESLINE": 41,
                "WHIRLWIND": 42,
                "SENTINEL": 43,
                "BARRICADE": 44,
                "HEAVY BLADE": 45,
                "RAGE": 46,
                "FIEND FIRE": 47,
                "PUMMEL": 48,
                "HEMOKINESIS": 49,
                "DEMON FORM": 50,
                "UPPERCUT": 51,
                "JUGGERNAUT": 52,
                "SPOT WEAKNESS": 53,
                "FIRE BREATHING": 54,
                "SECOND WIND": 55,
                "IMPERVIOUS": 56,
                "CLEAVE": 57,
                "SEARING BLOW": 58,
                "IMMOLATE": 59,
                "BLOOD FOR BLOOD": 60,
                "CLASH": 61,
                "BLOODLETTING": 62,
                "ARMAMENTS": 63,
                "RAMPAGE": 64,
                "ANGER": 65,
                "RUPTURE": 66,
                "METALLICIZE": 67,
                "CARNAGE": 68,
                "CORRUPTION": 69,
                "BATTLE TRANCE": 70,
                "TWIN STRIKE": 71,
                "GHOSTLY ARMOR": 72,
                "SHRUG IT OFF": 73,
                "POMMEL STRIKE": 74,
            },
            "index": {
                0: "HEADBUTT",
                1: "BRUTALITY",
                2: "BLUDGEON",
                3: "LIMIT BREAK",
                4: "EXHUME",
                5: "DOUBLE TAP",
                6: "TRUE GRIT",
                7: "BODY SLAM",
                8: "FEEL NO PAIN",
                9: "SEVER SOUL",
                10: "WILD STRIKE",
                11: "STRIKE_R",
                12: "BURNING PACT",
                13: "ENTRENCH",
                14: "INTIMIDATE",
                15: "DROPKICK",
                16: "PERFECTED STRIKE",
                17: "BERSERK",
                18: "INFERNAL BLADE",
                19: "WARCRY",
                20: "FEED",
                21: "RECKLESS CHARGE",
                22: "SEEING RED",
                23: "POWER THROUGH",
                24: "REAPER",
                25: "DEFEND_R",
                26: "HAVOC",
                27: "DUAL WIELD",
                28: "EVOLVE",
                29: "FLAME BARRIER",
                30: "OFFERING",
                31: "SHOCKWAVE",
                32: "FLEX",
                33: "BASH",
                34: "INFLAME",
                35: "SWORD BOOMERANG",
                36: "IRON WAVE",
                37: "THUNDERCLAP",
                38: "DISARM",
                39: "DARK EMBRACE",
                40: "COMBUST",
                41: "CLOTHESLINE",
                42: "WHIRLWIND",
                43: "SENTINEL",
                44: "BARRICADE",
                45: "HEAVY BLADE",
                46: "RAGE",
                47: "FIEND FIRE",
                48: "PUMMEL",
                49: "HEMOKINESIS",
                50: "DEMON FORM",
                51: "UPPERCUT",
                52: "JUGGERNAUT",
                53: "SPOT WEAKNESS",
                54: "FIRE BREATHING",
                55: "SECOND WIND",
                56: "IMPERVIOUS",
                57: "CLEAVE",
                58: "SEARING BLOW",
                59: "IMMOLATE",
                60: "BLOOD FOR BLOOD",
                61: "CLASH",
                62: "BLOODLETTING",
                63: "ARMAMENTS",
                64: "RAMPAGE",
                65: "ANGER",
                66: "RUPTURE",
                67: "METALLICIZE",
                68: "CARNAGE",
                69: "CORRUPTION",
                70: "BATTLE TRANCE",
                71: "TWIN STRIKE",
                72: "GHOSTLY ARMOR",
                73: "SHRUG IT OFF",
                74: "POMMEL STRIKE",
            },
        }

        if not weights or not os.path.exists(os.path.abspath(weights)):
            self.weights = np.ones((75, 75))
        else:
            self.weights = np.load(weights)

    def choose_card(self, potential_choices):
        """
        Takes in potential card choices as list and returns a card to select
        :param potential_choices: list of cards to select
        :return: single card to select
        """
        current_deck = self.vectorize_deck().reshape(1, -1)  # (1,75 deck)
        choices = {}
        if len(potential_choices) <= 0:
            return 0
        else:
            card_weights = current_deck @ self.weights
            card_weights = card_weights.reshape(-1)
            for card in potential_choices:
                name = card.name
                name = name.replace("+", "").upper()

                idx = self.card_index_dict["cards"].get(name)

                weight = card_weights[idx]

                choices[weight] = card

            choice = choices.get(np.max(list(choices.keys())))
            if choice:
                self.update_deck(choice.name.upper())
                return choice
            return 0

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
            if card_count > 1:
                self.deck["card"] -= 1
            elif card_count == 1:
                self.deck.pop("card")
            return

        if self.deck.get(card):
            self.deck[card] += 1
        else:
            self.deck[card] = 1
        self.deck_pick[len(self.deck_pick)] = card
        return

    def vectorize_deck(self):
        """
        Converts deck to numpy vector
        :return: numpy array with count in idx of cards, 0s elsewhere
        """
        indeces = list(map(self.card_index_dict["cards"].get, self.deck.keys()))

        deck_vector = np.zeros(75)

        for idx, count in zip(indeces, self.deck.values()):
            if not idx:
                continue
            deck_vector[idx] = count

        return deck_vector.astype(int)

    def unvectorize_deck(self, deck_vector):
        """
        Converts np vector of deck to deck dictionary
        :param deck_vector: deck vector, either shape 75, or 1,75
        :return: dict, card:count = K:V
        """
        if deck_vector.size != 75:
            print("Wrong vector shape, must be 75 cards!!")
            raise ValueError
        deck_vector.reshape(-1)
        # values, idx = np.unique(deck_vector, return_index=True)
        idx = deck_vector.nonzero()
        counts = deck_vector[idx]
        cards = list(map(self.card_index_dict["index"].get, idx[0]))

        return {card: int(count) for card, count in zip(cards, counts)}

    def dump_weights(self, timestamp):
        """
        Dumps card weights to npy file to load later with same timestamp as other runs
        :param timestamp: timestamp str of epoch time.
        :return: weights_timestamp.npy file in same dir as script is run
        """
        np.save(f"weights_{timestamp}", self.weights)

    def update_weights(self, n_updates=10, learning_rate=0.1):
        """
        Randomly adjusts weights in card weight matrix.
        :param n_updates:
        :param learning_rate:
        :return:
        """
        temp_weights = self.weights.astype(float)
        x_coord, y_coord = np.where(
            np.tril(temp_weights, -1) == 0
        )  # sets diag and upper to 0 and gives indeces
        coords = list(zip(x_coord, y_coord))
        weights_to_update = random.sample(coords, n_updates)
        temp_weights = np.triu(temp_weights)  # sets all values below diag to zero.

        for x, y in weights_to_update:
            temp_weights[x][y] = temp_weights[x][y] + (
                np.random.normal() * learning_rate
            )

        temp_weights = np.maximum(
            temp_weights, temp_weights.T
        )  # creates symmetric matrix from diag and upper

        self.weights = temp_weights


# main for testing model functions
if __name__ == "__main__":

    drafter = IroncladDraftModel()

    deck = drafter.vectorize_deck()
    print(drafter.unvectorize_deck(deck))
    drafter.update_deck("Pummel")
    print(drafter.deck)
    update = drafter.vectorize_deck()
