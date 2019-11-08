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
        self.deck = {"Bash": 1, "Strike_R": 5, "Defend_R": 4}
        self.floor = 0
        self.deck_pick = {}

        self.card_index_dict = {
            "cards": {
                "Headbutt": 0,
                "Brutality": 1,
                "Bludgeon": 2,
                "Limit Break": 3,
                "Exhume": 4,
                "Double Tap": 5,
                "True Grit": 6,
                "Body Slam": 7,
                "Feel No Pain": 8,
                "Sever Soul": 9,
                "Wild Strike": 10,
                "Strike_R": 11,
                "Burning Pact": 12,
                "Entrench": 13,
                "Intimidate": 14,
                "Dropkick": 15,
                "Perfected Strike": 16,
                "Berserk": 17,
                "Infernal Blade": 18,
                "Warcry": 19,
                "Feed": 20,
                "Reckless Charge": 21,
                "Seeing Red": 22,
                "Power Through": 23,
                "Reaper": 24,
                "Defend_R": 25,
                "Havoc": 26,
                "Dual Wield": 27,
                "Evolve": 28,
                "Flame Barrier": 29,
                "Offering": 30,
                "Shockwave": 31,
                "Flex": 32,
                "Bash": 33,
                "Inflame": 34,
                "Sword Boomerang": 35,
                "Iron Wave": 36,
                "Thunderclap": 37,
                "Disarm": 38,
                "Dark Embrace": 39,
                "Combust": 40,
                "Clothesline": 41,
                "Whirlwind": 42,
                "Sentinel": 43,
                "Barricade": 44,
                "Heavy Blade": 45,
                "Rage": 46,
                "Fiend Fire": 47,
                "Pummel": 48,
                "Hemokinesis": 49,
                "Demon Form": 50,
                "Uppercut": 51,
                "Juggernaut": 52,
                "Spot Weakness": 53,
                "Fire Breathing": 54,
                "Second Wind": 55,
                "Impervious": 56,
                "Cleave": 57,
                "Searing Blow": 58,
                "Immolate": 59,
                "Blood for Blood": 60,
                "Clash": 61,
                "Bloodletting": 62,
                "Armaments": 63,
                "Rampage": 64,
                "Anger": 65,
                "Rupture": 66,
                "Metallicize": 67,
                "Carnage": 68,
                "Corruption": 69,
                "Battle Trance": 70,
                "Twin Strike": 71,
                "Ghostly Armor": 72,
                "Shrug It Off": 73,
                "Pommel Strike": 74,
            },  # allows conversion from card to index and vice-versa
            "index": {
                0: "Headbutt",
                1: "Brutality",
                2: "Bludgeon",
                3: "Limit Break",
                4: "Exhume",
                5: "Double Tap",
                6: "True Grit",
                7: "Body Slam",
                8: "Feel No Pain",
                9: "Sever Soul",
                10: "Wild Strike",
                11: "Strike_R",
                12: "Burning Pact",
                13: "Entrench",
                14: "Intimidate",
                15: "Dropkick",
                16: "Perfected Strike",
                17: "Berserk",
                18: "Infernal Blade",
                19: "Warcry",
                20: "Feed",
                21: "Reckless Charge",
                22: "Seeing Red",
                23: "Power Through",
                24: "Reaper",
                25: "Defend_R",
                26: "Havoc",
                27: "Dual Wield",
                28: "Evolve",
                29: "Flame Barrier",
                30: "Offering",
                31: "Shockwave",
                32: "Flex",
                33: "Bash",
                34: "Inflame",
                35: "Sword Boomerang",
                36: "Iron Wave",
                37: "Thunderclap",
                38: "Disarm",
                39: "Dark Embrace",
                40: "Combust",
                41: "Clothesline",
                42: "Whirlwind",
                43: "Sentinel",
                44: "Barricade",
                45: "Heavy Blade",
                46: "Rage",
                47: "Fiend Fire",
                48: "Pummel",
                49: "Hemokinesis",
                50: "Demon Form",
                51: "Uppercut",
                52: "Juggernaut",
                53: "Spot Weakness",
                54: "Fire Breathing",
                55: "Second Wind",
                56: "Impervious",
                57: "Cleave",
                58: "Searing Blow",
                59: "Immolate",
                60: "Blood for Blood",
                61: "Clash",
                62: "Bloodletting",
                63: "Armaments",
                64: "Rampage",
                65: "Anger",
                66: "Rupture",
                67: "Metallicize",
                68: "Carnage",
                69: "Corruption",
                70: "Battle Trance",
                71: "Twin Strike",
                72: "Ghostly Armor",
                73: "Shrug It Off",
                74: "Pommel Strike",
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
        current_deck = self.vectorize_deck().reshape(1, -1) #(1,75 deck)
        choices = {}
        if len(potential_choices) <= 0:
            return 0
        else:
            card_weights = current_deck @ self.weights
            card_weights = card_weights.reshape(-1)
            for card in potential_choices:
                idx = self.card_index_dict['cards'].get(card.name)
                choices[card_weights[idx]] = card

            choice = choices.get(np.max(list(choices.keys())))
            if choice:
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
