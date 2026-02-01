
from flask import Flask, render_template, jsonify, request
from environment import StudyEnvironment
from q_learning_agent import QLearningAgent
import json
import os
import numpy as np

app = Flask(__name__)

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app.json_encoder = NumpyEncoder

# User preference defaults
PREFERENCE_DEFAULTS = {
    'fatigue_sensitivity': 'medium',
    'break_bias': 'study'
}

# Initialize RL environment and agent
env = StudyEnvironment()
env.set_preferences(PREFERENCE_DEFAULTS['fatigue_sensitivity'], PREFERENCE_DEFAULTS['break_bias'])
state = env.reset()
agent = QLearningAgent(state_size=(3, 3, 3, 3), action_size=3)

# Training state
training_state = {
    'is_training': False,
    'episodes_completed': 0,
    'total_episodes': 0,
    'rewards_history': [],
    'current_reward': 0
}

# Session history
session_history = {
    'total_sessions': 0,
    'total_study_time': 0,
    'sessions': [],  # List of {date, study_time, reward}
    'action_counts': {0: 0, 1: 0, 2: 0}  # Continue, Short Break, Long Break
}


def _get_history_path():
    explicit = os.getenv('DATA_PATH')
    if explicit:
        return explicit
    if os.getenv('VERCEL'):
        return '/tmp/session_history.json'
    return os.path.join(os.path.dirname(__file__), 'session_history.json')


def _load_session_history():
    global session_history
    path = _get_history_path()
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        action_counts = data.get('action_counts', {0: 0, 1: 0, 2: 0})
        if isinstance(action_counts, dict):
            action_counts = {int(k): int(v) for k, v in action_counts.items()}
        session_history = {
            'total_sessions': int(data.get('total_sessions', 0)),
            'total_study_time': int(data.get('total_study_time', 0)),
            'sessions': data.get('sessions', []),
            'action_counts': {
                0: action_counts.get(0, 0),
                1: action_counts.get(1, 0),
                2: action_counts.get(2, 0)
            }
        }
    except Exception:
        return


def _save_session_history():
    path = _get_history_path()
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(session_history, file)
    except Exception:
        return

_load_session_history()

# Action mappings
ACTIONS = {
    0: {'name': 'Continue Studying', 'description': 'Keep studying for 10 more minutes', 'icon': '📚'},
    1: {'name': 'Short Break', 'description': 'Take a 5-minute break', 'icon': '☕'},
    2: {'name': 'Long Break', 'description': 'Take a 15-minute break', 'icon': '🛏️'}
}

# User preference defaults
PREFERENCE_DEFAULTS = {
    'fatigue_sensitivity': 'medium',
    'break_bias': 'study'
}


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current study session status."""
    return jsonify({
        'study_time': int(env.study_time),
        'fatigue': int(env.fatigue),
        'state': list(state),
        'actions': ACTIONS
    })


@app.route('/api/preferences', methods=['GET', 'POST'])
def preferences():
    """Get or update user preference configuration."""
    global state
    if request.method == 'GET':
        return jsonify({
            'fatigue_sensitivity': env.fatigue_pref,
            'break_bias': env.break_bias
        })

    data = request.get_json() or {}
    fatigue_pref = data.get('fatigue_sensitivity', PREFERENCE_DEFAULTS['fatigue_sensitivity'])
    break_bias = data.get('break_bias', PREFERENCE_DEFAULTS['break_bias'])

    valid_fatigue = {'low', 'medium', 'high'}
    valid_break = {'study', 'short', 'long'}

    if fatigue_pref not in valid_fatigue or break_bias not in valid_break:
        return jsonify({'error': 'Invalid preference values'}), 400

    env.set_preferences(fatigue_pref, break_bias)
    state = env.get_state()
    return jsonify({
        'fatigue_sensitivity': fatigue_pref,
        'break_bias': break_bias,
        'state': list(state)
    })


@app.route('/api/action', methods=['POST'])
def take_action():
    """Execute an action and get the next recommendation."""
    global state
    
    data = request.get_json()
    action = data.get('action', 0)
    
    if action not in [0, 1, 2]:
        return jsonify({'error': 'Invalid action'}), 400
    
    # Track action
    session_history['action_counts'][action] += 1
    _save_session_history()
    
    # Execute action
    next_state, reward, done = env.step(action)
    
    # Update agent
    agent.update(state, action, reward, next_state)
    state = next_state
    
    # Track reward for current session
    training_state['current_reward'] += reward
    
    return jsonify({
        'action': ACTIONS[action]['name'],
        'reward': reward,
        'done': done,
        'study_time': int(env.study_time),
        'fatigue': int(env.fatigue),
        'state': list(next_state),
        'recommended_action': int(agent.choose_action(next_state)) if not done else None
    })


@app.route('/api/recommendation')
def get_recommendation():
    """Get AI-recommended action based on current state."""
    action = int(agent.choose_action(state))
    return jsonify({
        'recommended_action': action,
        'action_name': ACTIONS[action]['name'],
        'action_description': ACTIONS[action]['description'],
        'action_icon': ACTIONS[action]['icon']
    })


@app.route('/api/train', methods=['POST'])
def train_agent():
    """Start or stop training the agent."""
    global training_state
    
    data = request.get_json()
    episodes = data.get('episodes', 100)
    
    training_state['is_training'] = True
    training_state['total_episodes'] = episodes
    training_state['episodes_completed'] = 0
    training_state['rewards_history'] = []
    training_state['current_reward'] = 0
    
    # Train agent
    for ep in range(episodes):
        state_train = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action = agent.choose_action(state_train)
            next_state, reward, done = env.step(action)
            agent.update(state_train, action, reward, next_state)
            state_train = next_state
            total_reward += reward
        
        training_state['rewards_history'].append(total_reward)
        training_state['episodes_completed'] = ep + 1
        training_state['current_reward'] = total_reward
    
    training_state['is_training'] = False
    return jsonify(training_state)


@app.route('/api/training-status')
def get_training_status():
    """Get current training progress."""
    return jsonify(training_state)


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset the study session."""
    global state, env
    
    # Record session
    if env.study_time > 0:
        from datetime import datetime
        session_history['total_sessions'] += 1
        session_history['total_study_time'] += env.study_time
        session_history['sessions'].append({
            'date': datetime.now().isoformat(),
            'study_time': env.study_time,
            'reward': training_state['current_reward']
        })
        _save_session_history()
    
    state = env.reset()
    training_state['current_reward'] = 0
    
    return jsonify({
        'message': 'Session reset',
        'study_time': int(env.study_time),
        'fatigue': int(env.fatigue),
        'state': list(state)
    })


@app.route('/api/stats')
def get_stats():
    """Get training statistics."""
    if not training_state['rewards_history']:
        return jsonify({
            'average_reward': 0,
            'max_reward': 0,
            'min_reward': 0,
            'episodes': 0,
            'rewards_history': []
        })
    
    rewards = training_state['rewards_history']
    return jsonify({
        'average_reward': sum(rewards) / len(rewards),
        'max_reward': max(rewards),
        'min_reward': min(rewards),
        'episodes': len(rewards),
        'rewards_history': rewards[-50:]  # Last 50 episodes
    })


@app.route('/api/learning-stats')
def get_learning_stats():
    """Get comprehensive learning statistics."""
    total_actions = sum(session_history['action_counts'].values())
    
    action_distribution = {}
    for action_id, count in session_history['action_counts'].items():
        percentage = (count / total_actions * 100) if total_actions > 0 else 0
        action_distribution[action_id] = {
            'name': ACTIONS[action_id]['name'],
            'count': count,
            'percentage': percentage
        }
    
    # Calculate average reward
    if session_history['sessions']:
        avg_reward = sum(s['reward'] for s in session_history['sessions']) / len(session_history['sessions'])
    else:
        avg_reward = 0
    
    # Sessions (all)
    recent_sessions = session_history['sessions']
    recent_sessions_formatted = []
    for session in recent_sessions:
        from datetime import datetime
        dt = datetime.fromisoformat(session['date'])
        recent_sessions_formatted.append({
            'date': dt.strftime('%m/%d/%Y, %I:%M:%S %p'),
            'study_time': session['study_time'],
            'reward': session['reward']
        })
    
    return jsonify({
        'total_sessions': session_history['total_sessions'],
        'total_study_time': session_history['total_study_time'],
        'average_reward': avg_reward,
        'action_distribution': action_distribution,
        'recent_sessions': recent_sessions_formatted
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
