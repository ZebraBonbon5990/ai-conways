import numpy as np

DEATH_FACTOR = 0
BIRTH_FACTOR = 1

EPISODES = 1
MAX_STEPS = 2

FIELD_WIDTH = 100
FIELD_HEIGHT = 100

STATES = ACTIONS = FIELD_WIDTH * FIELD_HEIGHT

LEARNING_RATE = 1
EPSILLON = 0.9 #Chance for random action
GAMMA = 1 #The wheigt of future rewards

Q_ARRAY = np.zeros((STATES, ACTIONS))

#Q[state, action] = Q[state, action] + LEARNING_RATE * (reward + GAMMA * np.max(Q[new_state, :]) - Q[state, action])

living_cells = [[25,25], [26,25], [27,25]] #list containing coordinates of living cells and the number of alive neighbours in form of [x, y, alive]

must_check = [] #list containing all dead cells that have at least one living neighbor
living_neighbors = []
birth_queue = []
death_queue = []


def must():
    for cell in living_cells:
        must_check.append(cell)
        living_neighbors.append(0)

        if [cell[0]+1, cell[1]] not in living_cells and [cell[0]+1, cell[1]] not in must_check:
            must_check.append([cell[0]+1, cell[1]])
            living_neighbors.append(0)
        if [cell[0], cell[1]+1] not in living_cells and [cell[0], cell[1]+1] not in must_check:
            must_check.append([cell[0], cell[1]+1])
            living_neighbors.append(0)
        if [cell[0]+1, cell[1]+1] not in living_cells and [cell[0]+1, cell[1]+1] not in must_check:
            must_check.append([cell[0]+1, cell[1]+1])
            living_neighbors.append(0)
        if [cell[0]-1, cell[1]] not in living_cells and [cell[0]-1, cell[1]] not in must_check:
            must_check.append([cell[0]-1, cell[1]])
            living_neighbors.append(0)
        if [cell[0], cell[1]-1] not in living_cells and [cell[0], cell[1]-1] not in must_check:
            must_check.append([cell[0], cell[1]-1])
            living_neighbors.append(0)
        if [cell[0]-1, cell[1]-1] not in living_cells and [cell[0]-1, cell[1]-1] not in must_check:
            must_check.append([cell[0]-1, cell[1]-1])
            living_neighbors.append(0)
        if [cell[0]-1, cell[1]+1] not in living_cells and [cell[0]-1, cell[1]+1] not in must_check:
            must_check.append([cell[0]-1, cell[1]+1])
            living_neighbors.append(0)
        if [cell[0]+1, cell[1]-1] not in living_cells and [cell[0]+1, cell[1]-1] not in must_check:
            must_check.append([cell[0]+1, cell[1]-1])
            living_neighbors.append(0)


def count():
    for cell in must_check:
        if [cell[0]+1, cell[1]] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0], cell[1]+1] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0]+1, cell[1]+1] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0]-1, cell[1]] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0], cell[1]-1] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0]-1, cell[1]-1] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0]-1, cell[1]+1] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        if [cell[0]+1, cell[1]-1] in living_cells:
            living_neighbors[must_check.index(cell)] += 1
        

def update():
    global reward, next_state
    for i in range(len(living_neighbors)):
       # print(must_check[living_neighbors.index(neighbor)], neighbor)
        if living_neighbors[i] == 3 and (must_check[i] not in living_cells) and (ACTIONS-1) > must_check[i][0] >= 0 and (STATES-1) > must_check[i][1] >= 0:
            #print(must_check[i])
            birth_queue.append(must_check[i])

    for n in range(len(living_neighbors)):
        if (living_neighbors[n] > 3 or living_neighbors[n] < 2) and (must_check[n] in living_cells):
            death_queue.append(must_check[n])

    for cell in birth_queue:
        living_cells.append(cell)

    for cell in death_queue:
        living_cells.remove(cell)
    
    reward = BIRTH_FACTOR*len(birth_queue) - DEATH_FACTOR*len(death_queue)
    print(birth_queue)
    next_state = len(living_cells)

    must_check.clear()
    living_neighbors.clear()
    birth_queue.clear()
    death_queue.clear()


must()
count()
print(living_neighbors)

for i in range(EPISODES):
    
    living_cells.clear()

    for _ in range(MAX_STEPS):
        state = len(living_cells) -1

        if np.random.uniform(0, 1) > EPSILLON:
            action = np.random.randint(0, ACTIONS, dtype=np.int64)
        else:
            action = np.argmax(Q_ARRAY[state, :])

        update()
        print(living_cells)

        if [action, state] in living_cells:
            living_cells.remove([action.item() // STATES, action.item() % STATES])
        else:
            living_cells.append([action.item() // STATES, action.item() % STATES])

        
        must()
        count()
        
        Q_ARRAY[state, action] = Q_ARRAY[state, action] + LEARNING_RATE * (reward + GAMMA * np.max(Q_ARRAY[next_state, :]) - Q_ARRAY[state, action])

