# Mascarpone The Game

Finally Mascarpone is here!

# Mascarpone Game Implementation

A Python implementation of the Mascarpone card game, featuring agents (pretty dumb for the moment). This project uses Hydra for configuration management and provides detailed logging of game progression.

## 🌐 Play Online with Friends

Play Mascarpone with your friends online! Start a game server and share the link.

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
cd src
python web_server.py --port 5000
```

Then open `http://localhost:5000` in your browser.

### How to Play

#### Creating a Game
1. Enter your name
2. Click "Create New Game"
3. You'll be taken to a game lobby with a unique room code
4. Click "Copy Link" to share the room link with your friends
5. Once everyone has joined (minimum 2 players), click "Start Game"

#### Joining a Game
1. Enter your name
2. Enter the room code shared by your friend (or use the direct link they shared)
3. Click "Join Game"
4. Wait in the lobby until the host starts the game

#### Gameplay
1. **Declaration Phase**: Each player declares how many tricks they expect to win
   - The last player to declare cannot make the total equal to the number of cards
2. **Playing Phase**: Players take turns playing cards
   - Click on a card in your hand to play it
   - The highest card wins the trick
   - The trick winner leads the next trick
3. **Round End**: Players who didn't match their declaration are eliminated (Mascarpone!)
4. **Victory**: Last player standing wins!

### Command Line Options

```bash
python web_server.py --host 0.0.0.0 --port 5000 --debug
```

- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port number (default: 5000)
- `--debug`: Enable debug mode

### Deployment Tips

For playing with friends over the internet:
- Deploy on a cloud server (e.g., Heroku, Railway, DigitalOcean)
- Or use a tunneling service like ngrok: `ngrok http 5000`
- Share the public URL with your friends

## Project Overview

This implementation allows you to:

- **Play online with friends** via a web interface (no fancy graphics, just functional!)
- Run simulations of the Mascarpone card game with configurable  agents
- Track detailed game progression through comprehensive logging
- Customize game parameters through Hydra configuration

## Project Structure

```
mascarpone/
├── config/
│   ├── otherfoldersforconfig      # Default game parameters etc...
│   └── config.yaml                # Main configuration file
├── src/
│   ├── agents.py                  # AI agent implementations
│   ├── models.py                  # Card and game state models
│   ├── mascarpone.py              # Core game logic
│   ├── main.py                    # Entry point (simulation)
│   ├── web_server.py              # Web server for online play
│   ├── web_game.py                # Web game logic
│   ├── templates/                 # HTML templates
│   └── static/                    # CSS and JavaScript
└── README.md                      # This file
```



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


## Related Work

For a deep dive into optimal strategies of a particular scenario that may happen in Mascarpone (2 players, 2 cards), check out the companion repository [Mascarpone Strategy Analysis](https://github.com/danielelotito/mascarpone). This analysis:

- Evaluates optimal strategies for declaring 0, 1, or 2 tricks
- Provides probability calculations for different card combinations
- Includes visualization tools for strategy analysis
- Identifies winning positions and optimal play patterns

