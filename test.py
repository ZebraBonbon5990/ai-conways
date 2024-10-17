import pygame as pg
from matplotlib import pyplot as plt

living_cells = [[0,0], [1,0], [2,0]] #list containing coordinates of living cells in the form [x, y]

must_check = [] #list containing all cells which must be updated
living_neighbors = []
birth_queue = []
death_queue = []

fig = plt.figure()

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
    for i in range(len(living_neighbors)):
        #print(must_check[living_neighbors.index(neighbor)], neighbor)
        if living_neighbors[i] == 3 and (must_check[i] not in living_cells):
            #print(must_check[i])
            birth_queue.append(must_check[i])

    for n in range(len(living_neighbors)):
        if (living_neighbors[n] > 3 or living_neighbors[n] < 2) and (must_check[n] in living_cells):
            death_queue.append(must_check[n])

    for cell in birth_queue:
        living_cells.append(cell)

    for cell in death_queue:
        living_cells.remove(cell)
    
    print(len(birth_queue))

    must_check.clear()
    living_neighbors.clear()
    birth_queue.clear()
    death_queue.clear()


must()
count()
print(living_cells)
#print(must_check)
#print(living_neighbors)

for i in range(10):
    update()
    must()
    count()
    print(living_cells)
    plot = plt.scatter(*zip(*living_cells))
    plt.show(block=False)
    plt.pause(1)
    plt.close()
    #print(must_check)
    #print(living_neighbors)

plt.show()