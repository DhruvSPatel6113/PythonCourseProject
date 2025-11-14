import random
from enum import Enum, auto
from collections import Counter

class Suit(Enum):
    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank.name.capitalize()} of {self.suit.name.capitalize()}"

    def __lt__(self, other):
        return self.rank.value < other.rank.value

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        random.shuffle(self.cards)

    def draw(self, n=1):
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

HAND_RANKS = {
    "Royal Flush": 10,
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "Pair": 2,
    "High Card": 1,
}

def evaluate_hand(cards):
    """Returns (rank_name, rank_value) for a 5-card poker hand."""
    values = sorted([c.rank.value for c in cards])
    suits = [c.suit for c in cards]
    counts = Counter(values)
    is_flush = len(set(suits)) == 1
    is_straight = len(counts) == 5 and (max(values) - min(values) == 4)

    if set(values) == {10, 11, 12, 13, 14} and is_flush:
        return "Royal Flush", HAND_RANKS["Royal Flush"]
    elif is_straight and is_flush:
        return "Straight Flush", HAND_RANKS["Straight Flush"]
    elif 4 in counts.values():
        return "Four of a Kind", HAND_RANKS["Four of a Kind"]
    elif sorted(counts.values()) == [2, 3]:
        return "Full House", HAND_RANKS["Full House"]
    elif is_flush:
        return "Flush", HAND_RANKS["Flush"]
    elif is_straight:
        return "Straight", HAND_RANKS["Straight"]
    elif 3 in counts.values():
        return "Three of a Kind", HAND_RANKS["Three of a Kind"]
    elif list(counts.values()).count(2) == 2:
        return "Two Pair", HAND_RANKS["Two Pair"]
    elif 2 in counts.values():
        return "Pair", HAND_RANKS["Pair"]
    else:
        return "High Card", HAND_RANKS["High Card"]
