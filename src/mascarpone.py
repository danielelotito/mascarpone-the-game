import numpy as np
import logging
import sys
from typing import List, Dict, Tuple
from models import Card
from agents import AgentNaive

# Configure logging to handle Unicode and write to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('game_log.log', encoding='utf-8')
    ]
)

log = logging.getLogger(__name__)

class Mascarpone:
    def __init__(self, cfg):
        self.cfg = cfg
        self.n_players = cfg.game.N_players
        self.n_cards = cfg.game.N_cards
        self.initial_hand = cfg.game.Initial_hand
        
        # Game state
        self.current_round = 1
        self.cards_per_round = self.initial_hand
        self.active_players = list(range(self.n_players))
        
        # Calculate descending phase rounds
        self.descending_rounds = cfg.get('descending_rounds', self.initial_hand - 2)
        
        # Validate configuration
        self._validate_config()
        
        # Initialize deck and agents
        self.deck = self._create_deck()
        self.agents = self._initialize_agents()
        
        # Setup logging
        self._setup_logging()

    def _validate_config(self):
        """Validate game configuration parameters."""
        if self.n_players * self.initial_hand > self.n_cards:
            raise ValueError(
                f"Not enough cards for {self.n_players} players "
                f"with {self.initial_hand} cards each"
            )
        if not (self.cfg.game.min_players <= self.n_players <= self.cfg.game.max_players):
            raise ValueError(
                f"Number of players must be between "
                f"{self.cfg.game.min_players} and {self.cfg.game.max_players}"
            )
        if self.initial_hand < self.cfg.game.min_cards_per_hand:
            raise ValueError(
                f"Initial hand size ({self.initial_hand}) cannot be less than "
                f"minimum cards per hand ({self.cfg.game.min_cards_per_hand})"
            )

    def _create_deck(self) -> List[Card]:
        """Create and shuffle a new deck of cards."""
        deck = []
        for suit in self.cfg.game.suits:
            for value in range(self.cfg.game.card_min_value, 
                             self.cfg.game.card_max_value + 1):
                deck.append(Card(suit, value))
        np.random.shuffle(deck)
        return deck

    def _initialize_agents(self) -> List[AgentNaive]:
        """Initialize agents with their initial hands."""
        agents = []
        for i in range(self.n_players):
            start_idx = i * self.initial_hand
            end_idx = start_idx + self.initial_hand
            player_cards = self.deck[start_idx:end_idx]
            agents.append(AgentNaive(player_cards, self.cfg))
        return agents

    def _setup_logging(self):
        """Set up initial game logging."""
        log.info("=== Game Settings ===")
        log.info(f"Number of players: {self.n_players}")
        log.info(f"Initial hand size: {self.initial_hand}")
        log.info(f"Total cards: {self.n_cards}")
        log.info(f"Descending rounds: {self.descending_rounds}")
        log.info("\n=== Initial Hands ===")
        for i, agent in enumerate(self.agents):
            log.info(f"Agent {i} initial hand: {[str(card) for card in agent.cards]}")
        log.info("==================\n")

    def _update_cards_per_round(self):
        """Update the number of cards for the next round."""
        if self.current_round <= self.descending_rounds:
            # Descending phase
            self.cards_per_round = max(
                self.cfg.game.min_cards_per_hand,
                self.initial_hand - self.current_round + 1
            )
        else:
            # Ascending phase
            cards_to_add = self.current_round - self.descending_rounds
            self.cards_per_round = min(
                self.cfg.game.max_cards_per_hand,
                self.cfg.game.min_cards_per_hand + cards_to_add - 1
            )

    def _collect_declarations(self) -> List[int]:
        """Collect trick declarations from all active players."""
        declarations = []
        total_declared = 0
        
        for i, player_idx in enumerate(self.active_players):
            # Get declaration from agent
            is_last = i == len(self.active_players) - 1
            declaration = self.agents[player_idx].declare_tricks(
                total_declared, 
                self.cards_per_round,
                is_last
            )
            
            declarations.append(declaration)
            total_declared += declaration
            
            # Log the declaration along with current hand
            hand_str = [str(card) for card in self.agents[player_idx].cards]
            log.info(f"Agent {player_idx} {hand_str}: declares {declaration}")
        
        return declarations
    def _deal_cards(self):
        """Deal cards to players for the current round."""
        self.deck = self._create_deck()  # Reshuffle deck
        for i, player_idx in enumerate(self.active_players):
            start_idx = i * self.cards_per_round
            end_idx = start_idx + self.cards_per_round
            self.agents[player_idx].cards = self.deck[start_idx:end_idx]
            log.info(f"Agent {player_idx} hand: {[str(card) for card in self.agents[player_idx].cards]}")

    def trick_winner(self, pile: List[Tuple[int, Card]]) -> int:
        """Determine the winner of a trick."""
        highest_card_idx = 0
        for i in range(1, len(pile)):
            if pile[i][1] > pile[highest_card_idx][1]:
                highest_card_idx = i
        return highest_card_idx

    def _play_round(self):
        """Play a complete round of the game."""
        log.info(f"\n=== Round {self.current_round} ===")
        log.info(f"Cards per hand: {self.cards_per_round}")
        
        # Deal cards
        self._deal_cards()
        
        # Collect declarations
        log.info("\n--- Trick Declaration Phase ---")
        declarations = self._collect_declarations()
        
        # Play tricks
        for trick_num in range(self.cards_per_round):
            log.info(f"\n--- Trick {trick_num + 1}/{self.cards_per_round} ---")
            pile = []
            
            # Each player plays a card
            for player_idx in self.active_players:
                card = self.agents[player_idx].play(pile)
                pile.append((player_idx, card))
                log.info(f"Agent {player_idx} plays: {str(card)}")
            
            # Determine winner
            winner_idx = self.trick_winner(pile)
            winner_player = pile[winner_idx][0]
            self.agents[winner_player].tricks += 1
            
            log.info(f"Pile: {[(p, str(c)) for p, c in pile]}")
            log.info(f"Winning card: {str(pile[winner_idx][1])}")
            log.info(f"Winner: Agent {winner_player}")
        
        # Check eliminations
        log.info("\n--- Round Results ---")
        self._check_eliminations(declarations)

    def _check_eliminations(self, declarations: List[int]):
        """Check which players are eliminated this round."""
        log.info("Comparing tricks won vs declared:")
        eliminated = []
        
        for i, player_idx in enumerate(self.active_players):
            agent = self.agents[player_idx]
            log.info(f"Agent {player_idx}: [{agent.tricks} vs {declarations[i]}]")
            
            if agent.tricks != declarations[i]:
                eliminated.append(player_idx)
                log.info(f"Agent {player_idx} does MASCARPONE!")
            
            # Reset tricks for next round
            agent.tricks = 0
        
        # Remove eliminated players
        for player_idx in eliminated:
            self.active_players.remove(player_idx)
        
        log.info(f"Remaining Players: {self.active_players}")

    def play_game(self):
        """Play the complete game until a winner is determined."""
        while len(self.active_players) > 1:
            # Check if we have enough cards for this round
            if len(self.active_players) * self.cards_per_round > self.n_cards:
                log.warning(
                    f"Not enough cards for {len(self.active_players)} players "
                    f"with {self.cards_per_round} cards each. "
                    "Reducing cards per round."
                )
                self.cards_per_round -= 1
                continue
            
            self._play_round()
            self._update_cards_per_round()
            self.current_round += 1
        
        if self.active_players:
            log.info(f"\n Winner: Agent {self.active_players[0]}")
        else:
            log.info("\nGame ended with no winners!")