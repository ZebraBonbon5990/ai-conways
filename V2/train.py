import numpy as np
from matplotlib import pyplot as plt
import json
import time

# --- Configuration ---
FIELD_WIDTH = 50  # Reduced for faster training
FIELD_HEIGHT = 50
EPISODES = 10000
MAX_STEPS = 200

# Q-learning parameters
LEARNING_RATE = 0.2
GAMMA = 0.9
EPSILON_START = 1.0
EPSILON_END = 0.01
EPSILON_DECAY = 0.9999  # Slower decay

# Reward shaping
BIRTH_FACTOR = 0.5 #encourages creating living cells
DEATH_FACTOR = 1 #discourages killing cells
STABILITY_REWARD = 5  # Reward for achieving stable patterns
OSCILLATION_REWARD = 2  # Reward for achieving oscillating patterns
PATTERN_REWARDS = {  # Example rewards for specific patterns
    "glider": 10,
    "blinker": 5,
    # ... add more patterns in the future maybe
}

# State and action definitions
N_DENSITY_BINS = 5  # Number of bins for density
REGION_SIZE = 5  # Size of each region
N_REGIONS_X = FIELD_WIDTH // REGION_SIZE
N_REGIONS_Y = FIELD_HEIGHT // REGION_SIZE
N_ACTIONS = 9  # 3x3 grid centered around a random living cell

# Initialize Q-table and other variables
Q_ARRAY = {}
REWARD_PLOT = []
EPSILON = EPSILON_START
living_cells = []
previous_living_cells = []
history = []
MAX_HISTORY = 5

fig = plt.figure()

def initialize_field(pattern="random"):
    global living_cells
    living_cells = []
    if pattern == "random":
        for x in range(FIELD_WIDTH):
            for y in range(FIELD_HEIGHT):
                if np.random.random() < 0.3:  # Adjust density
                    living_cells.append((x, y))
    # Add other initial patterns here if needed
    elif pattern == "glider":
        living_cells = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]

def count_neighbors(cell):
    x, y = cell
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nx, ny = x + i, y + j
            if (nx, ny) in living_cells:
                count += 1
    return count

def update():
    global living_cells, previous_living_cells, history
    
    # Store previous state for stability/oscillation checks
    previous_living_cells = living_cells.copy()

    new_living_cells = []
    cells_to_check = set(living_cells)
    for cell in living_cells:
        for i in range(-1, 2):
            for j in range(-1, 2):
                cells_to_check.add((cell[0] + i, cell[1] + j))

    births = 0
    deaths = 0
    for cell in cells_to_check:
        neighbors = count_neighbors(cell)
        if cell in living_cells:
            if 2 <= neighbors <= 3:
                new_living_cells.append(cell)
            else:
                deaths += 1
        else:
            if neighbors == 3:
                new_living_cells.append(cell)
                births += 1

    living_cells = new_living_cells

    # Add current state to history
    history.append(set(living_cells))
    if len(history) > MAX_HISTORY:
        history.pop(0)

    return births, deaths

def calculate_reward(births, deaths):
    reward = BIRTH_FACTOR * births - DEATH_FACTOR * deaths

    # Check for stability
    if set(living_cells) == set(previous_living_cells):
        reward += STABILITY_REWARD

    # Check for oscillation
    if len(history) >= 2 and set(living_cells) in history[:-1]:
        reward += OSCILLATION_REWARD

    # Check for specific patterns (example)
    if is_glider():
        reward += PATTERN_REWARDS["glider"]
    if is_blinker():
        reward += PATTERN_REWARDS["blinker"]

    return reward

def is_glider():
    # Very basic glider detection (for demonstration)
    if len(living_cells) == 5:
        return True  # Could be more specific
    return False

def is_blinker():
    # Very basic blinker detection
    if len(living_cells) == 3:
        return True
    return False

def get_density():
    return len(living_cells) / (FIELD_WIDTH * FIELD_HEIGHT)

def get_state():
    regions = []
    for i in range(0, FIELD_WIDTH, REGION_SIZE):
        for j in range(0, FIELD_HEIGHT, REGION_SIZE):
            region_cells = [
                cell
                for cell in living_cells
                if i <= cell[0] < i + REGION_SIZE and j <= cell[1] < j + REGION_SIZE
            ]
            density = len(region_cells) / (REGION_SIZE * REGION_SIZE)
            density_bin = int(density * N_DENSITY_BINS)
            regions.append(density_bin)

    if set(living_cells) == set(previous_living_cells):
        pattern_type = 0  # Stable
    elif len(history) >= 2 and set(living_cells) in history[:-1]:
        pattern_type = 1  # Oscillating
    elif is_glider():
        pattern_type = 2
    elif is_blinker():
        pattern_type = 3
    # ... add more pattern checks
    else:
        pattern_type = N_DENSITY_BINS - 1  # Unknown

    state = tuple(regions)
    state = state + (pattern_type,)

    if state not in Q_ARRAY.keys():
        Q_ARRAY[state] = np.zeros(N_ACTIONS)

    return state

def choose_action(state):
    if np.random.random() < EPSILON:
        return np.random.randint(N_ACTIONS)
    else:
        return np.argmax(Q_ARRAY[state])

def take_action(action):
    if not living_cells:
        return  # Handle empty field

    center_cell = living_cells[np.random.randint(len(living_cells))]
    x, y = center_cell
    grid_pos = action - 4  # -4 to center actions around 0
    dx = grid_pos // 3 - 1
    dy = grid_pos % 3 - 1
    target_cell = (x + dx, y + dy)

    if 0 <= target_cell[0] < FIELD_WIDTH and 0 <= target_cell[1] < FIELD_HEIGHT:
        if target_cell in living_cells:
            living_cells.remove(target_cell)
        else:
            living_cells.append(target_cell)

# Main training loop
for episode in range(EPISODES):
    initialize_field(pattern="glider")
    state = get_state()

    for step in range(MAX_STEPS):
        action = choose_action(state)
        take_action(action)
        births, deaths = update()
        reward = calculate_reward(births, deaths)
        next_state = get_state()

        # Q-learning update
        best_next_action = np.argmax(Q_ARRAY[next_state])
        td_target = reward + GAMMA * Q_ARRAY[next_state][best_next_action]
        td_error = td_target - Q_ARRAY[state][action]
        Q_ARRAY[state][action] += LEARNING_RATE * td_error

        state = next_state
        REWARD_PLOT.append(reward)

    EPSILON = max(EPSILON_END, EPSILON * EPSILON_DECAY)
    print(f"Episode {episode} finished. Epsilon: {EPSILON:.3f}")

# Save Q-table
dict_with_string_keys = {str(key): value.tolist() for key, value in Q_ARRAY.items()}
with open("q_table.json", "w") as f:
    json.dump(dict_with_string_keys, f)

# Plot rewards
plt.plot(REWARD_PLOT)
plt.xlabel("Step")
plt.ylabel("Reward")
plt.title("Rewards over Time")
plt.show()