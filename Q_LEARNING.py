import numpy as np
from matplotlib import pyplot as plt

DEATH_FACTOR = 0.5
BIRTH_FACTOR = 1

EPISODES = 15
MAX_STEPS = 100

FIELD_WIDTH = 100
FIELD_HEIGHT = 100

STATES = ACTIONS = FIELD_WIDTH * FIELD_HEIGHT

LEARNING_RATE = 1
EPSILLON = 0.9 #Chance for random action
GAMMA = 1 #The wheigt of future rewards

Q_ARRAY = np.zeros((STATES, ACTIONS))

START_FIELD = [[25,25], [26,25], [27,25]]

fig = plt.figure()

#Q[state, action] = Q[state, action] + LEARNING_RATE * (reward + GAMMA * np.max(Q[new_state, :]) - Q[state, action])

living_cells = START_FIELD #list containing coordinates of living cells and the number of alive neighbours in form of [x, y, alive]

must_check = [] #list containing all dead cells that have at least one living neighbor
living_neighbors = []
birth_queue = []
death_queue = []

REWARD_PLOT = []

iterabl = [-1, 0, 1]

def must():
    for cell in living_cells:
        for x in iterabl:
            for y in iterabl:
                if  [cell[0]+x, cell[1]+y] not in must_check:
                    must_check.append([cell[0]+x, cell[1]+y])
                    living_neighbors.append(0)

def count():
    for cell in must_check:
        for x in iterabl:
            for y in iterabl:
                if [cell[0]+x, cell[1]+y] in living_cells and (x != 0 or y != 0):
                    living_neighbors[must_check.index(cell)] += 1
        

def update():
    global reward, next_state
    for i in range(len(living_neighbors)):
        if living_neighbors[i] == 3 and (must_check[i] not in living_cells) and (ACTIONS-1) > must_check[i][0] >= 0 and (STATES-1) > must_check[i][1] >= 0:
            birth_queue.append(must_check[i])

    for n in range(len(living_neighbors)):
        if (living_neighbors[n] > 3 or living_neighbors[n] < 2) and (must_check[n] in living_cells):
            death_queue.append(must_check[n])

    for cell in birth_queue:
        living_cells.append(cell)

    for cell in death_queue:
        living_cells.remove(cell)
    
    reward = BIRTH_FACTOR*len(birth_queue) - DEATH_FACTOR*len(death_queue)
    next_state = len(living_cells)

    must_check.clear()
    living_neighbors.clear()
    birth_queue.clear()
    death_queue.clear()


must()
count()
#print(living_neighbors)

for i in range(EPISODES):
    for _ in range(MAX_STEPS):
        state = len(living_cells) - 1

        if np.random.uniform(0, 1) < EPSILLON:
            action = np.random.randint(0, ACTIONS, dtype=np.int64)
        else:
            action = np.argmax(Q_ARRAY[state, :])

        update()
        #print(living_cells)

        if [action.item() // FIELD_WIDTH, action.item() % FIELD_HEIGHT] in living_cells:
            living_cells.remove([action.item() // FIELD_WIDTH, action.item() % FIELD_HEIGHT])
        else:
            living_cells.append([action.item() // FIELD_WIDTH, action.item() % FIELD_HEIGHT])

        
        must()
        count()
        REWARD_PLOT.append(reward)
        
        Q_ARRAY[state, action] = Q_ARRAY[state, action] + LEARNING_RATE * (reward + GAMMA * np.max(Q_ARRAY[next_state, :]) - Q_ARRAY[state, action])

    print(i)
    living_cells = START_FIELD
    EPSILLON -= 0.9/EPISODES

plot = plt.scatter(range(len(REWARD_PLOT)), REWARD_PLOT)
plt.show()