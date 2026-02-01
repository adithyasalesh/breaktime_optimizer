# 📚 Study Break Optimizer - RL Edition

A professional web application that uses **Reinforcement Learning (Q-Learning)** to provide intelligent study break recommendations. The system learns optimal break timing based on study duration and fatigue levels.

## 🎯 Features

- **AI-Powered Recommendations**: Q-Learning agent suggests optimal break times
- **Interactive Dashboard**: Real-time monitoring of study sessions
- **Agent Training**: Train the RL agent with custom episode counts
- **Performance Analytics**: Track training progress with reward charts
- **Responsive Design**: Works on desktop and mobile devices
- **RESTful API**: Clean API for all operations

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **ML Framework**: NumPy
- **Visualization**: Chart.js

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone/Download the project
```bash
cd StudyBreakOptimizer_RL
```

### 2. Create a virtual environment (optional but recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
Navigate to: **http://localhost:5000**

## 📖 How to Use

### Session Management
1. **View Status**: Monitor current study time and fatigue level
2. **Get Recommendations**: AI suggests your next action (Continue/Short Break/Long Break)
3. **Take Actions**: Follow recommendations to get reward feedback
4. **Reset Session**: Start a fresh study session anytime

### Training the Agent
1. Set the number of episodes (default: 100)
2. Click "Start Training"
3. Watch the progress bar and performance metrics update
4. View reward trends in the chart

### Actions Available
- **Continue Studying** (📚): Keep studying for 10 more minutes
- **Short Break** (☕): Take a 5-minute break to reduce fatigue
- **Long Break** (🛏️): Take a 15-minute break for deeper recovery

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Get current session status |
| POST | `/api/action` | Execute an action |
| GET | `/api/recommendation` | Get AI recommendation |
| POST | `/api/train` | Train agent for N episodes |
| GET | `/api/training-status` | Get training progress |
| GET | `/api/stats` | Get training statistics |
| POST | `/api/reset` | Reset session |

### Example: Take an Action
```bash
curl -X POST http://localhost:5000/api/action \
  -H "Content-Type: application/json" \
  -d '{"action": 1}'
```

## 🤖 Reinforcement Learning Details

### Algorithm
- **Type**: Q-Learning
- **States**: 9 possible states (3 time levels × 3 fatigue levels)
- **Actions**: 3 actions (Continue/Short Break/Long Break)
- **Hyperparameters**:
  - Learning Rate (α): 0.1
  - Discount Factor (γ): 0.9
  - Exploration Rate (ε): 0.2

### Training
- Episodes: Configurable (default 100)
- Each episode runs until study_time ≥ 120 minutes
- Rewards: Actions give immediate feedback (-1 for studying, +2/+4 for breaks)

## 📁 Project Structure

```
StudyBreakOptimizer_RL/
├── app.py                    # Flask application
├── environment.py            # Study environment
├── q_learning_agent.py      # Q-Learning agent
├── train.py                 # Training script (legacy)
├── ui.py                    # Tkinter UI (legacy)
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── templates/
│   └── index.html          # Main web interface
└── static/
    ├── style.css           # Styling
    └── script.js           # Frontend logic
```

## 🔧 Configuration

Modify hyperparameters in `q_learning_agent.py`:
```python
self.alpha = 0.1      # Learning rate
self.gamma = 0.9      # Discount factor
self.epsilon = 0.2    # Exploration rate
```

Adjust environment parameters in `environment.py`:
```python
# Time thresholds
if self.study_time < 30:  # Change 30 to adjust
    time_state = 0
```

## 📈 Performance Tips

1. **Train more episodes** for better performance
2. **Monitor the rewards chart** to see learning progress
3. **Adjust hyperparameters** if convergence is slow
4. **Reset sessions** frequently to collect diverse training data

## 🐛 Troubleshooting

### Port already in use
Change the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Module not found errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 🚀 Deployment

### Production Deployment (Gunicorn)
```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

## 📝 License

This project is proprietary and strictly belongs to the author. All rights reserved. No use, reproduction, modification, or distribution is permitted without explicit written permission.

## 👨‍💻 Author

Created as a Reinforcement Learning demonstration project.

## 🤝 Contributing

Feel free to fork, modify, and improve this project!

---

**Happy studying with AI! 🚀**
