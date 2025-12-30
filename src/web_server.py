"""
Web server for online Mascarpone multiplayer game.
Uses Flask and Flask-SocketIO for real-time communication.
"""
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from web_game import GameManager

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
socketio = SocketIO(app, cors_allowed_origins="*")

# Game manager instance
game_manager = GameManager()


@app.route('/')
def index():
    """Home page with options to create or join a game."""
    return render_template('index.html')


@app.route('/game/<room_id>')
def game_room(room_id):
    """Game room page."""
    game = game_manager.get_game(room_id)
    if not game:
        return render_template('error.html', message='Game room not found'), 404
    return render_template('game.html', room_id=room_id)


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    pass


@socketio.on('create_room')
def handle_create_room(data):
    """Create a new game room."""
    room_id = game_manager.create_room()
    emit('room_created', {'room_id': room_id})


@socketio.on('join_room')
def handle_join_room(data):
    """Join an existing game room."""
    room_id = data.get('room_id')
    player_name = data.get('player_name', 'Anonymous')
    
    if not room_id:
        emit('error', {'message': 'Room ID is required'})
        return
    
    game = game_manager.get_game(room_id)
    if not game:
        emit('error', {'message': 'Game room not found'})
        return
    
    # Generate player ID from socket session
    player_id = request.sid
    
    if not game.add_player(player_id, player_name):
        if player_id in game.players:
            # Player reconnecting
            join_room(room_id)
            join_room(player_id)  # Join personal room for direct messages
            emit('joined', {'room_id': room_id, 'player_id': player_id})
            emit('game_state', game.get_player_state(player_id))
            return
        emit('error', {'message': 'Cannot join game (full or already started)'})
        return
    
    join_room(room_id)
    join_room(player_id)  # Join personal room for direct messages
    emit('joined', {'room_id': room_id, 'player_id': player_id})
    
    # Broadcast updated player list to all players in room
    _broadcast_game_state(game)


@socketio.on('leave_room')
def handle_leave_room(data):
    """Leave a game room."""
    room_id = data.get('room_id')
    player_id = request.sid
    
    game = game_manager.get_game(room_id)
    if game:
        game.remove_player(player_id)
        leave_room(room_id)
        _broadcast_game_state(game)


@socketio.on('start_game')
def handle_start_game(data):
    """Start the game."""
    room_id = data.get('room_id')
    
    game = game_manager.get_game(room_id)
    if not game:
        emit('error', {'message': 'Game room not found'})
        return
    
    if len(game.players) < game.min_players:
        emit('error', {'message': f'Need at least {game.min_players} players to start'})
        return
    
    if not game.start_game():
        emit('error', {'message': 'Cannot start game'})
        return
    
    _broadcast_game_state(game)


@socketio.on('declare_tricks')
def handle_declare_tricks(data):
    """Handle trick declaration."""
    room_id = data.get('room_id')
    tricks = data.get('tricks')
    player_id = request.sid
    
    if tricks is None:
        emit('error', {'message': 'Tricks value is required'})
        return
    
    game = game_manager.get_game(room_id)
    if not game:
        emit('error', {'message': 'Game room not found'})
        return
    
    result = game.declare_tricks(player_id, int(tricks))
    
    if not result['success']:
        emit('error', {'message': result['error']})
        return
    
    _broadcast_game_state(game)


@socketio.on('play_card')
def handle_play_card(data):
    """Handle playing a card."""
    room_id = data.get('room_id')
    card_index = data.get('card_index')
    ace_low = data.get('ace_low', False)
    player_id = request.sid
    
    if card_index is None:
        emit('error', {'message': 'Card index is required'})
        return
    
    game = game_manager.get_game(room_id)
    if not game:
        emit('error', {'message': 'Game room not found'})
        return
    
    result = game.play_card(player_id, int(card_index), ace_low)
    
    if not result['success']:
        emit('error', {'message': result['error']})
        return
    
    # Broadcast game update
    if result.get('trick_complete'):
        socketio.emit('trick_result', {
            'winner': result['winner'],
            'winner_name': result['winner_name'],
            'pile': result['pile']
        }, room=room_id)
    
    if result.get('round_complete'):
        socketio.emit('round_result', {
            'round_summary': result['round_summary'],
            'eliminated': result['eliminated']
        }, room=room_id)
    
    if result.get('game_over'):
        socketio.emit('game_over', {
            'winner': result['game_winner']
        }, room=room_id)
    
    _broadcast_game_state(game)


@socketio.on('next_round')
def handle_next_round(data):
    """Start the next round."""
    room_id = data.get('room_id')
    
    game = game_manager.get_game(room_id)
    if not game:
        emit('error', {'message': 'Game room not found'})
        return
    
    if not game.next_round():
        emit('error', {'message': 'Cannot start next round'})
        return
    
    _broadcast_game_state(game)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    # Note: In a production app, you'd want to handle reconnection
    # For now, we leave the player in the game for potential reconnection
    pass


def _broadcast_game_state(game):
    """Broadcast game state to all players in a room."""
    for player_id in game.players:
        state = game.get_player_state(player_id)
        socketio.emit('game_state', state, room=player_id)


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the web server."""
    print(f"\n🎮 Mascarpone Web Server starting...")
    print(f"📱 Open http://localhost:{port} to play!")
    print(f"🔗 Share this link with friends to play together\n")
    if debug:
        # Development mode: allow Werkzeug's development server
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    else:
        # Production mode: use proper WSGI server
        socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Mascarpone Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, debug=args.debug)
