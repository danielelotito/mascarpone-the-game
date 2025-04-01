from dataclasses import dataclass


@dataclass
class Card:
    suit: str
    value: int

    # Suit values according to game rules
    SUIT_VALUES = {'♥': 4, '♦': 3, '♣': 2, '♠': 1}

    # Value mappings for face cards
    VALUE_MAPPING = {
        1: 'A',
        11: 'J',
        12: 'Q',
        13: 'K'
    }

    def __str__(self) -> str:
        # Use ASCII representations for suits to avoid encoding issues
        ASCII_SUITS = {'♥': 'H', '♦': 'D', '♣': 'C', '♠': 'S'}
        value_str = self.VALUE_MAPPING.get(self.value, str(self.value))
        return f"{value_str}{ASCII_SUITS[self.suit]}"

    def __lt__(self, other: 'Card') -> bool:
        # Special case for Ace of Hearts
        if self.suit == '♥' and self.value == 1:
            return False  # Ace of Hearts is never less than another card
        if other.suit == '♥' and other.value == 1:
            return True  # All cards are less than Ace of Hearts

        # Compare suits first
        if self.suit != other.suit:
            return self.SUIT_VALUES[self.suit] < self.SUIT_VALUES[other.suit]

        # Then compare values
        return self.value < other.value

    def __gt__(self, other: 'Card') -> bool:
        return other < self

    def __eq__(self, other: 'Card') -> bool:
        return self.suit == other.suit and self.value == other.value
