import random

class StudyEnvironment:
    def __init__(self):
        self.study_time = 0
        self.fatigue = 0
        self.fatigue_pref = 'medium'  # low, medium, high
        self.break_bias = 'study'     # study, short, long
        self.fatigue_pref_idx = 1
        self.break_bias_idx = 0

    def get_state(self):
        if self.study_time < 30:
            time_state = 0
        elif self.study_time < 60:
            time_state = 1
        else:
            time_state = 2

        if self.fatigue < 3:
            fatigue_state = 0
        elif self.fatigue < 6:
            fatigue_state = 1
        else:
            fatigue_state = 2

        return (time_state, fatigue_state, self.fatigue_pref_idx, self.break_bias_idx)

    def set_preferences(self, fatigue_sensitivity: str, break_bias: str):
        valid_fatigue = {'low': 0, 'medium': 1, 'high': 2}
        valid_break = {'study': 0, 'short': 1, 'long': 2}

        if fatigue_sensitivity in valid_fatigue:
            self.fatigue_pref = fatigue_sensitivity
            self.fatigue_pref_idx = valid_fatigue[fatigue_sensitivity]

        if break_bias in valid_break:
            self.break_bias = break_bias
            self.break_bias_idx = valid_break[break_bias]

    def step(self, action):
        # Reward shaping includes user preferences for fatigue sensitivity
        # and break bias to personalize the policy.
        reward = 0

        # Preference multipliers
        fatigue_weights = {'low': 0.6, 'medium': 1.0, 'high': 1.5}
        break_bias_bonus = {'study': 0.5, 'short': 0.3, 'long': 0.3}
        break_bias_penalty = {'study': 0.4, 'short': 0.2, 'long': 0.2}

        fatigue_weight = fatigue_weights.get(self.fatigue_pref, 1.0)

        # Helper scores
        fatigue_penalty = -0.5 * fatigue_weight * max(self.fatigue - 3, 0)
        progress_bonus = 0.6  # reward for making study-time progress

        if action == 0:  # continue studying
            self.study_time += 10
            self.fatigue += 1
            reward = 1.5 + progress_bonus + fatigue_penalty
            if self.break_bias == 'study':
                reward += break_bias_bonus['study']

        elif action == 1:  # short break
            self.fatigue = max(0, self.fatigue - 2)
            reward = 0.5
            if self.fatigue >= 4:
                reward += 1.0  # good recovery choice
            else:
                reward -= 0.5  # unnecessary early break

            if self.break_bias == 'short':
                reward += break_bias_bonus['short']
            elif self.break_bias == 'study':
                reward -= break_bias_penalty['study']

        elif action == 2:  # long break
            self.fatigue = max(0, self.fatigue - 4)
            reward = -0.5  # base cost for time lost
            if self.fatigue >= 6:
                reward += 1.5  # strong relief when very tired
            else:
                reward -= 1.2  # discourage long breaks while fresh

            if self.break_bias == 'long':
                reward += break_bias_bonus['long']
            elif self.break_bias == 'study':
                reward -= break_bias_penalty['study']

        done = self.study_time >= 120
        return self.get_state(), reward, done

    def reset(self):
        self.study_time = 0
        self.fatigue = 0
        return self.get_state()
