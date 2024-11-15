import numpy as np
import pygame as pg
from matplotlib import pyplot as plt
import json
import time

pg.init()
display = pg.display.set_mode((1000, 1000))

CELL_WIDTH = 10

print("Starting")

DEATH_FACTOR = 0.5      #factor that determines how much of a negative reward the ai recieves when a cell dies
BIRTH_FACTOR = 1        #factor that determines how much of a positive reward the ai recieves when a cell is born

EPISODES = 150       #how often the ai plays the game from the beginning on.
MAX_STEPS = 100     #how many steps/ticks there are per Episode

FIELD_WIDTH = 100       #The width of the field
FIELD_HEIGHT = 100      #The height of the field

STATES = FIELD_WIDTH * FIELD_HEIGHT #The amount of States and Actions there are in the game. (Number of alive cells, hence max the total amount of cells)

ACTIONS = FIELD_HEIGHT

LEARNING_RATE = 0.1 #multiplies the total reward gained
EPSILLON = 1 #Chance for random action to be taken
GAMMA = 1 #The weight of future rewards


START_FIELD = [[25,25], [26,25], [27,25]] #the coords of the cells alive at the beginning

cell_ages = np.zeros((FIELD_WIDTH, FIELD_HEIGHT), dtype=np.int64) #a matrix containing the age of every individual, living cell

fig = plt.figure()

#Q[state, action] = Q[state, action] + LEARNING_RATE * (reward + GAMMA * np.max(Q[new_state, :]) - Q[state, action])

living_cells = START_FIELD #list containing coordinates of living cells and the number of alive neighbours in form of [x, y, alive]

must_check = [] #list containing all dead cells that have at least one living neighbor
living_neighbors = []
birth_queue = []
death_queue = []

iterabl = [-1, 0, 1]

action = [0, 0, 0]

def update_cell_ages():
    for cell in living_cells:
        cell_ages[cell[0], cell[1]] += 1    # increment the age of all living cells
    
    for x in range(FIELD_WIDTH):
        for y in range(FIELD_HEIGHT):
            if [x, y] not in living_cells:
                cell_ages[x, y] = 0         #reset age of dead cells


def count_rim_cells():
    rim_cell_count = 0
    for x in living_neighbors:
        if x < 8:
            rim_cell_count += 1     #If a living cell has less than 8 living neighbours, It must have at leasr 1 dead neighbor -> it is a rim cell
    return rim_cell_count


def flood_fill(x, y, checked):
    if not (0 <= x < FIELD_WIDTH and 0 <= y < FIELD_HEIGHT) or checked[x][y] or [x, y] not in living_cells:  #if the cell is outside of the field, already go checked or is dead, just return 0
        return 0
    
    checked[x][y] = True    #mark cell as checked
    size = 1
    for v in iterabl:
        for w in iterabl:
            if v != 0 or w != 0:
                size += flood_fill(x + v, y + w, checked)   #increase size by the return of flood_fill applied to all neighbors of original cell
    
    return size


def count_clusters():
    checked = np.zeros((FIELD_WIDTH, FIELD_HEIGHT), dtype=np.bool)  #create array with info on if a cell has been checked or not
    cluster_sizes = []         #contains sizes of all clusters
    for cell in living_cells:
        if not checked[cell[0], cell[1]]:
            cluster_size = flood_fill(cell[0], cell[1], checked)    #start flood fill algorithm on any living cell which hasn't been checked yet
            cluster_sizes.append(cluster_size)
    
    num_clusters = len(cluster_sizes)
    avg_cluster_size = sum(cluster_sizes) / num_clusters if num_clusters > 0 else 0     #calculate average cluster size
    return num_clusters, avg_cluster_size


def load_model(model_file): #add model path. Models won't be on git-hub, because they are too large    
    path = model_file
    with open(path, "r") as file: 
        raw_data = json.load(file)
        Q_ARRAY = {eval(key.replace("(", "").replace(")", "")): [np.array(value[0]), np.array(value[1]), np.array(value[2])] for key, value in raw_data.items()}

    return Q_ARRAY


def get_state():        #takes all the components of the games state and returns a tuple containing them.
    num_living_cells = len(living_cells)
    total_neighbors = len(living_neighbors)
    num_clusters, avg_cluster_size = count_clusters()
    num_rim_cells = count_rim_cells()
    avg_cell_age = np.mean(cell_ages[cell_ages > 0]) if len(living_cells) == 0 else 0

    state = (num_living_cells, total_neighbors, num_clusters, avg_cluster_size, num_rim_cells, avg_cell_age)

    return state


def must():     #determines which cells must be updated
    for cell in living_cells:
        for x in iterabl:
            for y in iterabl:
                if  [cell[0]+x, cell[1]+y] not in must_check:
                    must_check.append([cell[0]+x, cell[1]+y])
                    living_neighbors.append(0)

def count_living_neighbors():    #counts the living neighbors of the cells which must be updated
    for cell in must_check:
        for x in iterabl:
            for y in iterabl:
                if [cell[0]+x, cell[1]+y] in living_cells and (x != 0 or y != 0):
                    living_neighbors[must_check.index(cell)] += 1

def update():
    global reward, next_state
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


def take_action():
    if state not in ai.keys():
        action[0] = np.random.randint(0, ACTIONS, dtype=np.int64)  #random x-Coordinate
        action[1] = np.random.randint(0, ACTIONS, dtype=np.int64)  #random y-Coordinate
        action[2] = np.random.randint(0, 2, dtype=np.int64) #random if to take another action
    else:
        #print("Ai action")
        print(next(iter(ai)))
        action[0] = np.argmax(ai[state][0])  #determine best x-Coordinate
        action[1] = np.argmax(ai[state][1])  #determine best y-Coordinate
        action[2] = np.argmax(ai[state][2])  #determine if to take another action

    if [action[0].item(), action[1].item()] in living_cells:
        living_cells.remove([action[0].item(), action[1].item()])
    else:
        living_cells.append([action[0].item(), action[1].item()])
    
    if action[2] == 1:
        take_action()


ai = load_model("sample10.json")

living_cells = START_FIELD

must()
count_living_neighbors()
for _ in range(MAX_STEPS):
    state = get_state()

    display.fill((0, 0, 0))

    for cell in living_cells:
        pg.draw.rect(display, (255, 255, 255), (cell[0]*CELL_WIDTH,cell[1]*CELL_WIDTH, CELL_WIDTH, CELL_WIDTH))

    pg.display.update()
    time.sleep(0.5)

    take_action()

    update()

    must()
    count_living_neighbors()

    
#EPSILLON *= 0.997