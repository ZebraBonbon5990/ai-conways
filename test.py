import pygame as pg

living_cells = [[0,0], [1,0], [2,0]] #list containing coordinates of living cells and the number of alive neighbours in form of [x, y, alive]

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
    for i in range(len(living_neighbors)):
       # print(must_check[living_neighbors.index(neighbor)], neighbor)
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
    #print(must_check)
    #print(living_neighbors)
