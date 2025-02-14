import numpy as np
import logging
from typing import List, Tuple
from models import Card

log = logging.getLogger(__name__)

class AgentNaive:
    """
    This agent sees the cards on the pile and plays the higher card in their hand that is still
    lower than the highest card in the pile. If they have no card that fits this criteria,
    they play the highest card in their hand.
    If the agent is first to play, they play the lowest card in their hand.
    """
    
    def __init__(self, cards: list, cfg):
        self.cfg = cfg
        self.name = "Naive"
        self.cards = cards
        self.tricks = 0
        self.trick_history = []
    
    def play(self, card_pile: List[Tuple[int, 'Card']]) -> 'Card':
        """Play a card based on the current pile state."""
        if not card_pile:  # First to play
            chosen_card = min(self.cards)
        else:
            # Find highest card in pile
            highest_pile_card = max(card[1] for card in card_pile)
            
            # Find cards in hand lower than highest pile card
            playable_cards = [card for card in self.cards if card < highest_pile_card]
            
            if playable_cards:  # If we have cards lower than highest
                chosen_card = max(playable_cards)
            else:  # If we must play higher
                chosen_card = max(self.cards)
        
        # Remove and return the chosen card
        self.cards.remove(chosen_card)
        return chosen_card