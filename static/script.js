// Global state
let currentChart = null;
let isTraining = false;
let currentReward = 0;
let stepCount = 0;
let sessionGoal = 120; // Default 120 minutes
let lastNotificationTime = 0;
let fatiguePref = 'medium';
let breakBias = 'study';
let currentRecommendation = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    goToPage('home');
});

/**
 * Navigate between pages
 */
function goToPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const pageId = pageName === 'home' ? 'home-page' : 
                   pageName === 'how-it-works' ? 'how-it-works-page' : 
                   pageName === 'statistics' ? 'statistics-page' :
                   'monitor-page';
    
    document.getElementById(pageId).classList.add('active');

    // If going to monitor, initialize the session
    if (pageName === 'monitor') {
        initializeMonitor();
    }
    
    // If going to statistics, load stats
    if (pageName === 'statistics') {
        loadLearningStats();
    }
}

/**
 * Initialize monitor page
 */
function initializeMonitor() {
    currentReward = 0;
    stepCount = 0;
    requestNotificationPermission();
    loadPreferences();
    
    // Load saved session goal
    const saved = localStorage.getItem('sessionGoal');
    if (saved) {
        sessionGoal = parseInt(saved);
        document.getElementById('session-goal').value = sessionGoal;
    }
    document.getElementById('goal-target').textContent = sessionGoal;
    
    updateMonitorStatus();
    updateRecommendation();
    updateStats();
}

/**
 * Update customizable session goal
 */
function updateSessionGoal() {
    const newGoal = parseInt(document.getElementById('session-goal').value);
    if (newGoal > 0 && newGoal <= 480) {
        sessionGoal = newGoal;
        localStorage.setItem('sessionGoal', sessionGoal);
        document.getElementById('goal-target').textContent = sessionGoal;
        const currentStudy = parseInt(document.getElementById('monitor-study-time').textContent || '0');
        updateGoalProgress(currentStudy); // Update progress bar based on backend
        showNotification('✅', 'Session goal updated to ' + sessionGoal + ' minutes');
    } else {
        alert('Please enter a valid goal between 30 and 480 minutes');
    }
}

/**
 * Show browser notification
 */
function showNotification(icon, message) {
    // Check if enough time has passed since last notification
    const now = Date.now();
    if (now - lastNotificationTime < 5000) return; // Prevent spam
    lastNotificationTime = now;
    
    // Browser notification (with permission)
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(icon + ' Study Break Optimizer', {
            body: message,
            icon: '📚'
        });
    }
    
    // In-page notification
    showInPageNotification(icon, message);
}

/**
 * Show in-page notification
 */
function showInPageNotification(icon, message) {
    const notif = document.createElement('div');
    notif.className = 'notification-popup';
    notif.innerHTML = `<span>${icon}</span> ${message}`;
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => notif.remove(), 300);
    }, 4000);
}

/**
 * Request notification permission
 */
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

/**
 * Fetch and update current session status
 */
async function updateMonitorStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        document.getElementById('monitor-study-time').textContent = data.study_time;
        document.getElementById('monitor-fatigue-level').textContent = data.fatigue;
        document.getElementById('monitor-steps').textContent = 'Step ' + stepCount;
        updateGoalProgress(data.study_time);
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

/**
 * Load saved preferences from backend
 */
async function loadPreferences() {
    try {
        const res = await fetch('/api/preferences');
        const prefs = await res.json();
        fatiguePref = prefs.fatigue_sensitivity || 'medium';
        breakBias = prefs.break_bias || 'study';

        const fatigueSelect = document.getElementById('fatigue-pref');
        const breakSelect = document.getElementById('break-bias');
        if (fatigueSelect) fatigueSelect.value = fatiguePref;
        if (breakSelect) breakSelect.value = breakBias;
    } catch (err) {
        console.error('Error loading preferences:', err);
    }
}

/**
 * Save preferences to backend
 */
async function savePreferences() {
    const fatigueSelect = document.getElementById('fatigue-pref');
    const breakSelect = document.getElementById('break-bias');
    const payload = {
        fatigue_sensitivity: fatigueSelect ? fatigueSelect.value : 'medium',
        break_bias: breakSelect ? breakSelect.value : 'study'
    };

    try {
        const res = await fetch('/api/preferences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Failed to save preferences');
        const prefs = await res.json();
        fatiguePref = prefs.fatigue_sensitivity;
        breakBias = prefs.break_bias;
        showNotification('✅', 'Preferences saved');
    } catch (err) {
        console.error('Error saving preferences:', err);
        alert('Could not save preferences.');
    }
}

/**
 * Fetch and display AI recommendation
 */
async function updateRecommendation() {
    try {
        const response = await fetch('/api/recommendation');
        const data = await response.json();

        currentRecommendation = data;

        document.getElementById('rec-icon').textContent = data.action_icon;
        document.getElementById('rec-action').textContent = data.action_name;
        document.getElementById('rec-description').textContent = data.action_description;
    } catch (error) {
        console.error('Error updating recommendation:', error);
    }
}

/**
 * Take the recommended action
 */
async function takeAction() {
    try {
        if (!currentRecommendation) {
            await updateRecommendation();
        }

        const action = currentRecommendation?.recommended_action;
        if (action === undefined || action === null) {
            throw new Error('No recommendation available');
        }

        const actionResponse = await fetch('/api/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action })
        });

        const data = await actionResponse.json();

        currentReward += data.reward;
        stepCount += 1;
        updateGoalProgress(data.study_time);

        // Check if it's a break recommendation
        if (action === 1 || action === 2) {
            showNotification('☕', 'Time for a ' + (action === 1 ? 'short' : 'long') + ' break!');
        }

        // Check if reached goal
        if (data.study_time >= sessionGoal) {
            showNotification('🎉', 'Daily goal reached! Excellent work!');
        }

        if (data.done) {
            showNotification('✅', 'Session completed! Reward: ' + currentReward);
            alert(`Session completed! Final reward: ${currentReward}\nClick Next Step to start a new session.`);
            stepCount = 0;
            currentReward = 0;
        }

        updateMonitorStatus();
        updateRecommendation();
    } catch (error) {
        console.error('Error taking action:', error);
        alert('Error executing action');
    }
}

/**
 * Reset the study session
 */
async function resetSession() {
    try {
        await fetch('/api/reset', { method: 'POST' });
        currentReward = 0;
        stepCount = 0;
        updateMonitorStatus();
        alert('Session reset!');
    } catch (error) {
        console.error('Error resetting session:', error);
    }
}

/**
 * Update goal progress using backend study_time (step-based)
 */
function updateGoalProgress(studyTime) {
    const progressPercent = Math.min((studyTime / sessionGoal) * 100, 100);
    document.getElementById('progress-bar-fill').style.width = progressPercent + '%';
    document.getElementById('current-progress').textContent = studyTime;
}

/**
 * Toggle statistics panel visibility
 */
function toggleStatistics() {
    const panel = document.getElementById('statistics-panel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        updateStats();
    }
}

/**
 * Start training the agent
 */
async function startTraining() {
    if (isTraining) return;

    isTraining = true;
    const episodes = parseInt(document.getElementById('episodes').value);
    const trainBtn = document.getElementById('train-btn');
    const progressDiv = document.getElementById('training-progress');

    trainBtn.disabled = true;
    progressDiv.classList.remove('hidden');

    try {
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ episodes: episodes })
        });

        const data = await response.json();

        // Simulate progress updates
        const totalEpisodes = data.total_episodes;
        for (let ep = 0; ep <= totalEpisodes; ep++) {
            const progress = (ep / totalEpisodes) * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
            document.getElementById('training-status').textContent =
                `Completed: ${ep}/${totalEpisodes} episodes`;
            await new Promise(resolve => setTimeout(resolve, 10));
        }

        progressDiv.classList.add('hidden');
        trainBtn.disabled = false;
        isTraining = false;

        // Update stats
        updateStats();
        alert('Training completed!');
    } catch (error) {
        console.error('Error during training:', error);
        alert('Error during training');
        progressDiv.classList.add('hidden');
        trainBtn.disabled = false;
        isTraining = false;
    }
}

/**
 * Update training statistics and chart
 */
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        document.getElementById('avg-reward').textContent = data.average_reward.toFixed(2);
        document.getElementById('max-reward').textContent = data.max_reward.toFixed(2);
        document.getElementById('episodes-trained').textContent = data.episodes;

        // Update chart
        if (data.rewards_history && data.rewards_history.length > 0) {
            updateChart(data.rewards_history);
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

/**
 * Create or update the rewards chart
 */
function updateChart(rewardsHistory) {
    const canvas = document.getElementById('rewardsChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (currentChart) {
        currentChart.destroy();
    }

    const episodes = Array.from({ length: rewardsHistory.length }, (_, i) => i + 1);

    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: episodes,
            datasets: [{
                label: 'Reward per Episode',
                data: rewardsHistory,
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        usePointStyle: true,
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#ecf0f1'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Load learning statistics
 */
async function loadLearningStats() {
    try {
        const response = await fetch('/api/learning-stats');
        const data = await response.json();

        // Update top stats
        document.getElementById('total-sessions').textContent = data.total_sessions;
        document.getElementById('avg-reward-display').textContent = data.average_reward.toFixed(1);
        document.getElementById('total-study-time').textContent = data.total_study_time;

        // Update action distribution
        for (const [actionId, actionData] of Object.entries(data.action_distribution)) {
            document.getElementById(`action-${actionId}-percent`).textContent = actionData.percentage.toFixed(1) + '%';
            document.getElementById(`action-${actionId}-count`).textContent = actionData.count + ' times';
        }

        // Update recent sessions table
        const tbody = document.getElementById('sessions-tbody');
        if (data.recent_sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="no-data">No sessions yet. Start studying!</td></tr>';
        } else {
            tbody.innerHTML = data.recent_sessions.map(session => `
                <tr>
                    <td>${session.date}</td>
                    <td>${session.study_time} min</td>
                    <td>${session.reward}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading learning stats:', error);
    }
}
