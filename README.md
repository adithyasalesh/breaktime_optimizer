# Study Break Optimizer (Reinforcement Learning)

Study Break Optimizer is a Flask web app that uses a Q-learning agent to recommend the next best action during a study session: continue studying, take a short break, or take a long break.

The system models study-time progress, fatigue, and user preferences, then updates a Q-table over time to improve recommendations.

## 1) Project Overview

This project combines:
- A browser-based dashboard for session monitoring and interaction.
- A reinforcement learning environment that simulates fatigue and recovery.
- A Q-learning agent that learns state-action values from reward feedback.
- Session + action analytics persisted in JSON.

Core idea: optimize focus and recovery by making break timing adaptive instead of fixed.

## 2) Tech Stack

- Backend: Python + Flask
- RL/Math: NumPy
- Frontend: HTML, CSS, vanilla JavaScript
- Charts: Chart.js
- Persistence: JSON file (`session_history.json`, or `DATA_PATH` override)

## 3) RL Algorithm Concept

### 3.1 State Space
The environment state is a 4-tuple:
- `time_state` in `{0,1,2}` (derived from total study minutes)
- `fatigue_state` in `{0,1,2}`
- `fatigue_preference` in `{low, medium, high}` encoded as `{0,1,2}`
- `break_bias` in `{study, short, long}` encoded as `{0,1,2}`

Total states: `3 x 3 x 3 x 3 = 81`.

### 3.2 Action Space
- `0`: Continue Studying
- `1`: Short Break
- `2`: Long Break

### 3.3 Reward Design (Shaped)
Rewards are not binary; they are shaped to balance:
- Progress bonus from studying.
- Fatigue penalty when over-studying.
- Recovery benefit for breaks when fatigue is high.
- Personalization bonuses/penalties from user preference (`fatigue_sensitivity`, `break_bias`).

### 3.4 Learning Rule
Q-table update follows standard Q-learning:

`Q(s,a) <- Q(s,a) + alpha * (reward + gamma * max_a' Q(s',a') - Q(s,a))`

Default hyperparameters in `q_learning_agent.py`:
- `alpha = 0.1`
- `gamma = 0.9`
- `epsilon = 0.2`

## 4) User Manual

### 4.1 Setup
1. Open the project folder.
2. Create/activate your virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the web app:

```bash
python app.py
```

5. Open `http://localhost:5000`.

### 4.2 Navigation
- **Home**: Project intro and feature summary.
- **Monitor**: Live study session controls and AI recommendation.
- **Statistics**: Session history + action distribution.

### 4.3 Typical Study Session Flow
1. Go to **Monitor**.
2. Set your daily goal (30–480 minutes).
3. Set preferences:
   - Fatigue Sensitivity: Low / Medium / High
   - Break Bias: Prefer Studying / Short Breaks / Long Breaks
4. Click **Save Preferences**.
5. Use **Next Step** repeatedly to follow the AI recommendation cycle.
6. Watch live updates:
   - Study time
   - Fatigue level
   - Reward progression
7. Use **Reset Session** to end/start a fresh run.

### 4.4 Training the Agent in UI
1. In Monitor, open the statistics panel (**View Statistics**).
2. Enter episode count.
3. Click **Start Training**.
4. After training, review:
   - Average reward
   - Max reward
   - Episodes trained
   - Reward chart trend

### 4.5 Understanding Personalization
- `fatigue_sensitivity` changes how strongly fatigue affects rewards.
- `break_bias` nudges policy toward study, short breaks, or long breaks.
- Preferences affect both recommendation quality and learned Q-values.

## 5) API Quick Reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/status` | Current study time, fatigue, state |
| GET/POST | `/api/preferences` | Read/update personalization settings |
| GET | `/api/recommendation` | Next recommended action from agent |
| POST | `/api/action` | Execute action, get reward + next state |
| POST | `/api/train` | Train agent for N episodes |
| GET | `/api/training-status` | Current training progress snapshot |
| GET | `/api/stats` | Reward summary for training runs |
| POST | `/api/reset` | Reset current session |
| GET | `/api/learning-stats` | Aggregated sessions + action distribution |

## 6) Project Structure

```text
StudyBreakOptimizer_RL/
├── app.py
├── environment.py
├── q_learning_agent.py
├── train.py
├── visualize.py
├── requirements.txt
├── session_history.json
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## 7) Notes

- `session_history.json` stores aggregate learning/session history.
- You can override history path with environment variable `DATA_PATH`.
- In Vercel mode, history defaults to `/tmp/session_history.json`.
- `train.py` and `visualize.py` are standalone scripts and may require alignment with the current 4D state definition before use.
