# Mascarpone The Game

Finally Mascarpone is here!

# Mascarpone Game Implementation

A Python implementation of the Mascarpone card game, featuring agents (pretty dumb for the moment). This project uses Hydra for configuration management and provides detailed logging of game progression.

## Project Overview

This implementation allows you to:

- Run simulations of the Mascarpone card game with configurable  agents
- Track detailed game progression through comprehensive logging
- Customize game parameters through Hydra configuration

## Project Structure

```
mascarpone/
├── config/
│   ├── agent_setup_default.yaml   # Default agent configuration
│   ├── agent_naive.yaml           # Naive agent strategy settings
│   ├── game_default.yaml          # Default game parameters
│   └── config.yaml                # Main configuration file
├── src/
│   ├── agents.py                  # AI agent implementations
│   ├── models.py                  # Card and game state models
│   ├── mascarpone.py             # Core game logic
│   └── main.py                   # Entry point
└── README.md                     # This file
```

## Related Work

For a deep dive into optimal strategies in a simplified version of Mascarpone (2 players, 2 cards), check out the companion repository [Mascarpone Strategy Analysis](https://github.com/danielelotito/mascarpone). This analysis:

- Evaluates optimal strategies for declaring 0, 1, or 2 tricks
- Provides probability calculations for different card combinations
- Includes visualization tools for strategy analysis
- Identifies winning positions and optimal play patterns

# Mascarpone Card Game Rules

## 🎴 Overview

Mascarpone is an engaging card game where players must accurately predict and achieve their declared number of tricks. Making too many or too few tricks results in elimination ("Mascarpone"). The last player remaining wins!

## 📋 Requirements

- Standard 52-card French deck (no jokers)
- 2 to 10 players

## 🃏 Card Values

1. Suits (highest to lowest): Hearts ♥️ > Diamonds ♦️ > Clubs ♣️ > Spades ♠️
2. Card Order: A > K > Q > J > 10 > 9 > 8 > 7 > 6 > 5 > 4 > 3 > 2
3. Special Card: Ace of Hearts can be played as either the highest or lowest card (player's choice)

## 🎮 Game Structure

### Card Distribution by Round

#### Descending Phase

- Round 1: 5 cards
- Round 2: 4 cards
- Round 3: 3 cards
- Round 4: 2 cards

#### Ascending Phase

- Round 5: 3 cards
- Round 6: 4 cards
- Round 7: 5 cards
- Round 8: 6 cards
- Round 9: 7 cards

Note: Fewer rounds may be played depending on the number of players and game progression.

## 📜 Game Rules

1. At the start of each round, players declare their expected number of tricks
2. The dealer (last to declare) cannot make the total declared tricks equal to the number of cards per hand
3. Play proceeds clockwise, with each player playing one card
4. Highest card wins the trick; winner leads the next trick
5. Players not achieving their declared number of tricks are eliminated ("Mascarpone")

## 🏆 Victory

The last remaining player wins the game!
