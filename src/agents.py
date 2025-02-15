import numpy as np
import logging
from typing import List, Tuple
from models import Card

log = logging.getLogger(__name__)

class AgentNaive:
    """
    This agent declares a number of tricks equal to the number of hearts in their hand.
    When playing, it tries to play the highest card lower than the highest card in the pile.
    If no such card exists, it plays its highest card.
    If first to play, it plays its lowest card.
    """
    
    def __init__(self, cards: list, cfg):
        self.cfg = cfg
        self.name = "Naive"
        self.cards = cards
        self.tricks = 0
        self.trick_history = []
    
    def declare_tricks(self, total_declared: int, cards_per_round: int, is_last: bool) -> int:
        """
        Declare expected number of tricks based on hearts in hand.
        
        Args:
            total_declared: Sum of declarations made by previous players
            cards_per_round: Number of cards per player this round
            is_last: Whether this player is the last to declare
            
        Returns:
            int: Number of tricks declared
        """
        # Count hearts in hand
        hearts_count = sum(1 for card in self.cards if card.suit == '♥')
        
        if is_last:
            # Last player must ensure total declarations != cards_per_round
            remaining = cards_per_round - total_declared
            if remaining <= 0:  # Safety check
                return 0
                
            # Always pick a number different from remaining
            if hearts_count >= remaining:
                # If we have enough hearts, declare one less than remaining
                return remaining - 1
            else:
                # If we have fewer hearts than remaining, declare them all
                # unless that would make total = cards_per_round
                if hearts_count == remaining:
                    return hearts_count - 1
                return hearts_count
        else:
            # Other players declare based on hearts, bounded by available tricks
            max_declare = min(cards_per_round, cards_per_round - total_declared)
            return min(hearts_count, max_declare)
    
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