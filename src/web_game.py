"""
Web-based Mascarpone game logic for online multiplayer.
"""
import uuid
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from models import Card


@dataclass
class Player:
    """Represents a human player in the web game."""
    id: str
    name: str
    cards: List[Card] = field(default_factory=list)
    tricks_won: int = 0
    declared_tricks: Optional[int] = None
    is_eliminated: bool = False


class WebGame:
    """
    Manages a Mascarpone game session for web-based multiplayer.
    """
    # Card distribution pattern: descending then ascending
    CARD_PATTERN = [5, 4, 3, 2, 3, 4, 5, 6, 7]
    
    # Suit values for comparison
    SUIT_VALUES = {'♥': 4, '♦': 3, '♣': 2, '♠': 1}
    
    def __init__(self, room_id: str, min_players: int = 2, max_players: int = 10):
        self.room_id = room_id
        self.min_players = min_players
        self.max_players = max_players
        
        # Game state
        self.players: Dict[str, Player] = {}
        self.player_order: List[str] = []
        self.active_player_ids: List[str] = []
        
        # Phase and round tracking
        self.phase = 'waiting'  # waiting, declaring, playing, round_end, game_over
        self.current_round = 0
        self.cards_per_round = 0
        
        # Declaration tracking
        self.declarations: Dict[str, int] = {}
        self.current_declarer_idx = 0
        
        # Trick tracking
        self.current_trick = 0
        self.current_pile: List[Tuple[str, Card]] = []
        self.current_player_idx = 0
        self.trick_starter_idx = 0
        
        # Game history
        self.round_results: List[Dict] = []
    
    def add_player(self, player_id: str, name: str) -> bool:
        """Add a player to the game."""
        if self.phase != 'waiting':
            return False
        if len(self.players) >= self.max_players:
            return False
        if player_id in self.players:
            return False
        
        self.players[player_id] = Player(id=player_id, name=name)
        self.player_order.append(player_id)
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        if player_id not in self.players:
            return False
        
        del self.players[player_id]
        self.player_order.remove(player_id)
        if player_id in self.active_player_ids:
            self.active_player_ids.remove(player_id)
        return True
    
    def start_game(self) -> bool:
        """Start the game if enough players have joined."""
        if len(self.players) < self.min_players:
            return False
        if self.phase != 'waiting':
            return False
        
        self.active_player_ids = self.player_order.copy()
        self._start_round()
        return True
    
    def _create_deck(self) -> List[Card]:
        """Create and shuffle a standard 52-card deck."""
        deck = []
        for suit in ['♥', '♦', '♣', '♠']:
            for value in range(1, 14):  # 1 (Ace) to 13 (King)
                deck.append(Card(suit, value))
        random.shuffle(deck)
        return deck
    
    def _start_round(self):
        """Start a new round."""
        self.current_round += 1
        round_idx = min(self.current_round - 1, len(self.CARD_PATTERN) - 1)
        self.cards_per_round = self.CARD_PATTERN[round_idx]
        
        # Check if we have enough cards
        while len(self.active_player_ids) * self.cards_per_round > 52:
            self.cards_per_round -= 1
        
        # Deal cards
        deck = self._create_deck()
        for i, player_id in enumerate(self.active_player_ids):
            player = self.players[player_id]
            start_idx = i * self.cards_per_round
            end_idx = start_idx + self.cards_per_round
            player.cards = deck[start_idx:end_idx]
            player.tricks_won = 0
            player.declared_tricks = None
        
        # Reset round state
        self.declarations = {}
        self.current_declarer_idx = 0
        self.current_trick = 0
        self.current_pile = []
        self.trick_starter_idx = 0
        self.current_player_idx = 0
        
        self.phase = 'declaring'
    
    def get_current_declarer_id(self) -> Optional[str]:
        """Get the ID of the player who should declare next."""
        if self.phase != 'declaring':
            return None
        if self.current_declarer_idx >= len(self.active_player_ids):
            return None
        return self.active_player_ids[self.current_declarer_idx]
    
    def get_total_declared(self) -> int:
        """Get the sum of all declarations so far."""
        return sum(self.declarations.values())
    
    def is_last_declarer(self, player_id: str) -> bool:
        """Check if a player is the last to declare."""
        return self.current_declarer_idx == len(self.active_player_ids) - 1
    
    def declare_tricks(self, player_id: str, tricks: int) -> Dict:
        """
        Submit a trick declaration for a player.
        Returns a dict with success status and any error message.
        """
        if self.phase != 'declaring':
            return {'success': False, 'error': 'Not in declaration phase'}
        
        current_declarer = self.get_current_declarer_id()
        if player_id != current_declarer:
            return {'success': False, 'error': 'Not your turn to declare'}
        
        # Validate declaration
        if tricks < 0 or tricks > self.cards_per_round:
            return {'success': False, 'error': f'Invalid declaration (must be 0-{self.cards_per_round})'}
        
        # Last player cannot make total equal cards_per_round
        if self.is_last_declarer(player_id):
            total_so_far = self.get_total_declared()
            if total_so_far + tricks == self.cards_per_round:
                return {
                    'success': False,
                    'error': f'Cannot declare {tricks} - total would equal {self.cards_per_round}'
                }
        
        # Record declaration
        self.declarations[player_id] = tricks
        self.players[player_id].declared_tricks = tricks
        self.current_declarer_idx += 1
        
        # Check if all players have declared
        if self.current_declarer_idx >= len(self.active_player_ids):
            self.phase = 'playing'
            self.current_player_idx = self.trick_starter_idx
        
        return {'success': True}
    
    def get_current_player_id(self) -> Optional[str]:
        """Get the ID of the player whose turn it is to play."""
        if self.phase != 'playing':
            return None
        return self.active_player_ids[self.current_player_idx]
    
    def play_card(self, player_id: str, card_index: int, ace_low: bool = False) -> Dict:
        """
        Play a card from a player's hand.
        ace_low: If True and the card is Ace of Hearts, treat it as the lowest card.
        Returns a dict with success status, the played card, and any error message.
        """
        if self.phase != 'playing':
            return {'success': False, 'error': 'Not in playing phase'}
        
        current_player = self.get_current_player_id()
        if player_id != current_player:
            return {'success': False, 'error': 'Not your turn'}
        
        player = self.players[player_id]
        if card_index < 0 or card_index >= len(player.cards):
            return {'success': False, 'error': 'Invalid card index'}
        
        # Play the card
        card = player.cards.pop(card_index)
        self.current_pile.append((player_id, card, ace_low))
        
        # Move to next player
        self.current_player_idx = (self.current_player_idx + 1) % len(self.active_player_ids)
        
        # Check if trick is complete
        if len(self.current_pile) == len(self.active_player_ids):
            return self._resolve_trick(card)
        
        return {'success': True, 'card': str(card)}
    
    def _card_strength(self, card: Card, ace_low: bool = False) -> Tuple[int, int]:
        """
        Calculate card strength for comparison.
        Returns (suit_value, card_value) tuple.
        Ace of Hearts with ace_low=True is the weakest card.
        """
        suit_val = self.SUIT_VALUES[card.suit]
        
        # Ace of Hearts special handling
        if card.suit == '♥' and card.value == 1:
            if ace_low:
                return (0, 0)  # Lowest possible
            else:
                return (5, 14)  # Highest possible
        
        # Ace is normally 14 (highest)
        card_val = card.value if card.value != 1 else 14
        return (suit_val, card_val)
    
    def _resolve_trick(self, last_card: Card) -> Dict:
        """Determine the winner of the current trick."""
        # Find highest card
        best_idx = 0
        best_strength = self._card_strength(self.current_pile[0][1], self.current_pile[0][2])
        
        for i in range(1, len(self.current_pile)):
            player_id, card, ace_low = self.current_pile[i]
            strength = self._card_strength(card, ace_low)
            if strength > best_strength:
                best_strength = strength
                best_idx = i
        
        winner_id = self.current_pile[best_idx][0]
        self.players[winner_id].tricks_won += 1
        
        result = {
            'success': True,
            'card': str(last_card),
            'trick_complete': True,
            'winner': winner_id,
            'winner_name': self.players[winner_id].name,
            'pile': [(pid, str(c)) for pid, c, _ in self.current_pile]
        }
        
        # Prepare for next trick
        self.current_trick += 1
        self.current_pile = []
        
        # Set next trick starter to the winner
        self.trick_starter_idx = self.active_player_ids.index(winner_id)
        self.current_player_idx = self.trick_starter_idx
        
        # Check if round is complete
        if self.current_trick >= self.cards_per_round:
            return self._resolve_round(result)
        
        return result
    
    def _resolve_round(self, result: Dict) -> Dict:
        """End the round and check for eliminations."""
        eliminated = []
        round_summary = []
        
        for player_id in self.active_player_ids:
            player = self.players[player_id]
            declared = player.declared_tricks
            won = player.tricks_won
            
            player_result = {
                'player_id': player_id,
                'name': player.name,
                'declared': declared,
                'won': won,
                'mascarpone': declared != won
            }
            round_summary.append(player_result)
            
            if declared != won:
                player.is_eliminated = True
                eliminated.append(player_id)
        
        # Remove eliminated players
        for pid in eliminated:
            self.active_player_ids.remove(pid)
        
        self.round_results.append(round_summary)
        
        result['round_complete'] = True
        result['round_summary'] = round_summary
        result['eliminated'] = eliminated
        
        # Check for game over
        if len(self.active_player_ids) <= 1:
            self.phase = 'game_over'
            result['game_over'] = True
            if self.active_player_ids:
                winner = self.players[self.active_player_ids[0]]
                result['game_winner'] = {'id': winner.id, 'name': winner.name}
            else:
                result['game_winner'] = None
        else:
            self.phase = 'round_end'
        
        return result
    
    def next_round(self) -> bool:
        """Start the next round after round_end phase."""
        if self.phase != 'round_end':
            return False
        self._start_round()
        return True
    
    def get_player_state(self, player_id: str) -> Optional[Dict]:
        """Get the game state from a specific player's perspective."""
        if player_id not in self.players:
            return None
        
        player = self.players[player_id]
        
        # Other players' info (hide cards)
        other_players = []
        for pid in self.player_order:
            p = self.players[pid]
            other_players.append({
                'id': p.id,
                'name': p.name,
                'card_count': len(p.cards),
                'tricks_won': p.tricks_won,
                'declared_tricks': p.declared_tricks,
                'is_eliminated': p.is_eliminated,
                'is_you': pid == player_id
            })
        
        state = {
            'room_id': self.room_id,
            'phase': self.phase,
            'current_round': self.current_round,
            'cards_per_round': self.cards_per_round,
            'your_cards': [str(c) for c in player.cards],
            'your_tricks_won': player.tricks_won,
            'your_declared_tricks': player.declared_tricks,
            'is_eliminated': player.is_eliminated,
            'players': other_players,
            'active_player_ids': self.active_player_ids,
            'current_pile': [(pid, str(c)) for pid, c, _ in self.current_pile],
            'total_declared': self.get_total_declared(),
            'declarations': {pid: self.declarations.get(pid) for pid in self.active_player_ids}
        }
        
        if self.phase == 'declaring':
            state['current_declarer'] = self.get_current_declarer_id()
            state['is_your_turn'] = state['current_declarer'] == player_id
            state['is_last_declarer'] = self.is_last_declarer(player_id) if state['is_your_turn'] else False
        elif self.phase == 'playing':
            state['current_player'] = self.get_current_player_id()
            state['is_your_turn'] = state['current_player'] == player_id
        
        return state


class GameManager:
    """Manages multiple game rooms."""
    
    def __init__(self):
        self.games: Dict[str, WebGame] = {}
    
    def create_room(self) -> str:
        """Create a new game room and return its ID."""
        room_id = str(uuid.uuid4())[:8]
        self.games[room_id] = WebGame(room_id)
        return room_id
    
    def get_game(self, room_id: str) -> Optional[WebGame]:
        """Get a game by room ID."""
        return self.games.get(room_id)
    
    def remove_room(self, room_id: str):
        """Remove a game room."""
        if room_id in self.games:
            del self.games[room_id]
