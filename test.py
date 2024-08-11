import pygame as pg

living_cells = [[1,0], [0,1], [0,2], [1,2]] #list containing coordinates of living cells and the number of alive neighbours in form of [x, y, alive]
living_neighbors = [0, 0, 0, 0]

must_check = [] #list containing all dead cells 

def first_tick_count():
    for cell in living_cells:
        if [cell[0]+1, cell[1]] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0], cell[1]+1] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0]+1, cell[1]+1] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0]-1, cell[1]] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0], cell[1]-1] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0]-1, cell[1]-1] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0]-1, cell[1]+1] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        if [cell[0]+1, cell[1]-1] in living_cells:
            living_neighbors[living_cells.index(cell)] += 1
        

def update():
    for neighbor in living_neighbors:
        if neighbor > 3 or neighbor < 2:
            living_cells.pop(living_neighbors.index(neighbor))
            living_neighbors.pop(living_neighbors.index(neighbor))


first_tick_count()
print(living_cells)
print(living_neighbors)

update()
print(living_cells)
print(living_neighbors)