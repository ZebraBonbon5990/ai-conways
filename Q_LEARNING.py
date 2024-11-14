import numpy as np
from matplotlib import pyplot as plt
import json

DEATH_FACTOR = 0.5      #factor that determines how much of a negative reward the ai recieves when a cell dies
BIRTH_FACTOR = 1        #factor that determines how much of a positive reward the ai recieves when a cell is born

EPISODES = 1500       #how often the ai plays the game from the beginning on.
MAX_STEPS = 100     #how many steps/ticks there are per Episode

FIELD_WIDTH = 100       #The width of the field
FIELD_HEIGHT = 100      #The height of the field

STATES = FIELD_WIDTH * FIELD_HEIGHT #The amount of States and Actions there are in the game. (Number of alive cells, hence max the total amount of cells)

ACTIONS = FIELD_HEIGHT

LEARNING_RATE = 0.1 #multiplies the total reward gained
EPSILLON = 1 #Chance for random action to be taken
GAMMA = 1 #The weight of future rewards

Q_ARRAY = {} #create the ai

START_FIELD = [[25,25], [26,25], [27,25]] #the coords of the cells alive at the beginning

cell_ages = np.zeros((FIELD_WIDTH, FIELD_HEIGHT), dtype=np.int64) #a matrix containing the age of every individual, living cell

fig = plt.figure()

#Q[state, action] = Q[state, action] + LEARNING_RATE * (reward + GAMMA * np.max(Q[new_state, :]) - Q[state, action])

living_cells = START_FIELD #list containing coordinates of living cells and the number of alive neighbours in form of [x, y, alive]

must_check = [] #list containing all dead cells that have at least one living neighbor
living_neighbors = []
birth_queue = []
death_queue = []

REWARD_PLOT = []

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
    
    reward = BIRTH_FACTOR*len(birth_queue) - DEATH_FACTOR*len(death_queue)
    next_state = get_state()

    must_check.clear()
    living_neighbors.clear()
    birth_queue.clear()
    death_queue.clear()


def take_action():
    if np.random.uniform(0, 1) < EPSILLON:
        action[0] = np.random.randint(0, ACTIONS, dtype=np.int64)  #random x-Coordinate
        action[1] = np.random.randint(0, ACTIONS, dtype=np.int64)  #random y-Coordinate
        action[2] = np.random.randint(0, 2, dtype=np.int64) #random if to take another action
    else:
        action[0] = np.argmax(Q_ARRAY[state][0])  #determine best x-Coordinate
        action[1] = np.argmax(Q_ARRAY[state][1])  #determine best y-Coordinate
        action[2] = np.argmax(Q_ARRAY[state][2])  #determine if to take another action

    if [action[0].item(), action[1].item()] in living_cells:
        living_cells.remove([action[0].item(), action[1].item()])
    else:
        living_cells.append([action[0].item(), action[1].item()])
    
    if action[2] == 1:
        take_action()


must()
count_living_neighbors()

for i in range(EPISODES):
    for _ in range(MAX_STEPS):
        state = get_state()
        if state not in Q_ARRAY.keys():
            Q_ARRAY[state] = [np.zeros(ACTIONS), np.zeros(ACTIONS), np.zeros(2)]

        take_action()

        update()
        #print(living_cells)

        if next_state not in Q_ARRAY.keys():
            Q_ARRAY[next_state] = [np.zeros(ACTIONS), np.zeros(ACTIONS), np.zeros(2)]

        """
        if [action.item() // FIELD_WIDTH, action.item() % FIELD_HEIGHT] in living_cells:
            living_cells.remove([action.item() // FIELD_WIDTH, action.item() % FIELD_HEIGHT])
        else:
            living_cells.append([action.item() // FIELD_WIDTH, action.item() % FIELD_HEIGHT])
        """
        
        

        must()
        count_living_neighbors()
        REWARD_PLOT.append(reward)

        q_value_0 =Q_ARRAY[state][0][action[0]]
        q_value_1 = Q_ARRAY[state][1][action[1]]
        q_value_2 = Q_ARRAY[state][2][action[2]]
        
        Q_ARRAY[state][0][action[0]] = q_value_0 + LEARNING_RATE * (reward + GAMMA * np.max(Q_ARRAY[next_state][0]) - q_value_0)
        Q_ARRAY[state][1][action[1]] = q_value_1 + LEARNING_RATE * (reward + GAMMA * np.max(Q_ARRAY[next_state][1]) - q_value_1)
        Q_ARRAY[state][2][action[2]] = q_value_2 + LEARNING_RATE * (reward + GAMMA * np.max(Q_ARRAY[next_state][2]) - q_value_2)

    print(i)
    living_cells = START_FIELD
    EPSILLON *= 0.997

plot = plt.scatter(range(len(REWARD_PLOT)), REWARD_PLOT)
dict_with_string_keys = {str(key): [value[0].tolist(), value[1].tolist()] for key, value in Q_ARRAY.items()}
with open("sample1.json", "w") as outfile: 
   json.dump(dict_with_string_keys, outfile)
plt.show()