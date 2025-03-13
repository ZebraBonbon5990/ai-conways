import numpy as np
import pygame as pg
import json
import time

pg.init()

# --- Configuration ---
CELL_WIDTH = 10  # Width of each cell in pixels
FIELD_WIDTH = 50  # Width of the field in cells (adjust for visibility)
FIELD_HEIGHT = 50  # Height of the field in cells
MAX_STEPS = 200  # Number of steps per episode
MODEL_FILE = "q_table.json"  # Path to your saved Q-table
START_PATTERN = "glider"  # Starting pattern: "random" or "glider"

display = pg.display.set_mode((FIELD_WIDTH * CELL_WIDTH, FIELD_HEIGHT * CELL_WIDTH))

print("Starting")

# --- Game Logic ---
iterabl = [-1, 0, 1]
living_cells = []
must_check = []
living_neighbors = []
birth_queue = []
death_queue = []
cell_ages = np.zeros((FIELD_WIDTH, FIELD_HEIGHT), dtype=np.int64)

def initialize_field(pattern="random"):
    global living_cells
    living_cells = []
    if pattern == "random":
        for x in range(FIELD_WIDTH):
            for y in range(FIELD_HEIGHT):
                if np.random.random() < 0.3:  # Adjust density as needed
                    living_cells.append([x, y])
    elif pattern == "glider":
        glider_coords = [[1, 0], [2, 1], [0, 2], [1, 2], [2, 2]]
        for x, y in glider_coords:
            living_cells.append([x, y])

def update_cell_ages():
    for cell in living_cells:
        cell_ages[cell[0], cell[1]] += 1
    for x in range(FIELD_WIDTH):
        for y in range(FIELD_HEIGHT):
            if [x, y] not in living_cells:
                cell_ages[x, y] = 0

def count_rim_cells():
    rim_cell_count = 0
    for x in living_neighbors:
        if x < 8:
            rim_cell_count += 1
    return rim_cell_count

def flood_fill(x, y, checked):
    if not (0 <= x < FIELD_WIDTH and 0 <= y < FIELD_HEIGHT) or checked[x][y] or [x, y] not in living_cells:
        return 0
    checked[x][y] = True
    size = 1
    for v in iterabl:
        for w in iterabl:
            if v != 0 or w != 0:
                size += flood_fill(x + v, y + w, checked)
    return size

def count_clusters():
    checked = np.zeros((FIELD_WIDTH, FIELD_HEIGHT), dtype=np.bool)
    cluster_sizes = []
    for cell in living_cells:
        if not checked[cell[0], cell[1]]:
            cluster_size = flood_fill(cell[0], cell[1], checked)
            cluster_sizes.append(cluster_size)
    num_clusters = len(cluster_sizes)
    avg_cluster_size = sum(cluster_sizes) / num_clusters if num_clusters > 0 else 0
    return num_clusters, avg_cluster_size

def get_state():
    num_living_cells = len(living_cells)
    total_neighbors = len(living_neighbors)
    num_clusters, avg_cluster_size = count_clusters()
    num_rim_cells = count_rim_cells()
    avg_cell_age = np.mean(cell_ages[cell_ages > 0]) if len(cell_ages[cell_ages > 0]) == 0 else 0
    state = (num_living_cells, total_neighbors, num_clusters, avg_cluster_size, num_rim_cells, avg_cell_age)
    return state

def must():
    for cell in living_cells:
        for x in iterabl:
            for y in iterabl:
                if [cell[0] + x, cell[1] + y] not in must_check:
                    must_check.append([cell[0] + x, cell[1] + y])
                    living_neighbors.append(0)

def count_living_neighbors():
    for cell in must_check:
        for x in iterabl:
            for y in iterabl:
                if [cell[0] + x, cell[1] + y] in living_cells and (x != 0 or y != 0):
                    living_neighbors[must_check.index(cell)] += 1

def update():
    global next_state
    for i in range(len(living_neighbors)):
        if living_neighbors[i] == 3 and (must_check[i] not in living_cells) and (FIELD_WIDTH) > must_check[i][0] >= 0 and (FIELD_HEIGHT) > must_check[i][1] >= 0:
            birth_queue.append(must_check[i])
    for n in range(len(living_neighbors)):
        if (living_neighbors[n] > 3 or living_neighbors[n] < 2) and (must_check[n] in living_cells):
            death_queue.append(must_check[n])
    for cell in birth_queue:
        living_cells.append(cell)
    for cell in death_queue:
        living_cells.remove(cell)
    next_state = get_state()
    must_check.clear()
    living_neighbors.clear()
    birth_queue.clear()
    death_queue.clear()

# --- AI Logic ---
def load_model(model_file):
    path = model_file
    with open(path, "r") as file:
        raw_data = json.load(file)
        q_array = {eval(key.replace("(", "").replace(")", "")): [np.array(value[0]), np.array(value[1]), np.array(value[2])] for key, value in raw_data.items()}
    return q_array

def take_action():
    global queue_action, action
    ACTIONS = FIELD_HEIGHT
    if state not in ai.keys():
        action[0] = np.random.randint(0, ACTIONS, dtype=np.int64)
        action[1] = np.random.randint(0, ACTIONS, dtype=np.int64)
        action[2] = np.random.randint(0, 2, dtype=np.int64)
    else:
        print("Ai action")
        print(state)
        action[0] = np.argmax(ai[state][0])
        action[1] = np.argmax(ai[state][1])
        action[2] = np.argmax(ai[state][2])

    if [action[0].item(), action[1].item()] in living_cells:
        death_queue.append([action[0].item(), action[1].item()])
    else:
        birth_queue.append([action[0].item(), action[1].item()])
    if action[2] == 1:
        queue_action = True

# --- Main Loop ---
ai = load_model(MODEL_FILE)
initialize_field(pattern=START_PATTERN)
action = [0, 0, 0]

must()
count_living_neighbors()

for _ in range(MAX_STEPS):
    queue_action = True
    while queue_action:
        state = get_state()
        take_action()
        queue_action = False

    display.fill((0, 0, 0))
    for cell in living_cells:
        pg.draw.rect(display, (255, 255, 255), (cell[0] * CELL_WIDTH, cell[1] * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH))

    pg.display.update()
    time.sleep(0.1)  # Adjust for visualization speed

    update()
    must()
    count_living_neighbors()