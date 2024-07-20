# Imports
import matplotlib.pyplot as plt
import pygame
from random import randint as rand

# Variables
# Start arrays
entities=[]
# Field
field_size = 500
# Start nums
startnum_of_herbs = 100
startnum_of_predators = 5
startnum_of_vegetarians = 10

painting=True
play=True
stoper=50

# Functions
def ecostart():
    # Start arrays
    global entities, field_size
    entities = []
    # Start fieling
    for i in range(startnum_of_herbs):
        entities.append(Herb(rand(1, field_size*0.99), rand(1, field_size*0.99)))
    for i in range(startnum_of_predators):
        entities.append(Predator(rand(1, field_size*0.99), rand(1, field_size*0.99)))
    for i in range(startnum_of_vegetarians):
        entities.append(Vegetarian(rand(1, field_size*0.99), rand(1, field_size*0.99)))


def drawing():
    global entities

    game.fill((0,0,0))
    # Drawing points
    for (entity) in entities:
        entity.draw_circle()
    # Showing grafic
    win.blit(game,(25,25))
    pygame.display.update()

# Classes
class Biotic:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
    def drawcircle(self):
        pygame.draw.circle(game, self.color, (int(self.x),int(self.y)), self.markersize,0)


class Herb(Biotic):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "green"
        self.markersize = 10


class Predator(Biotic):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "red"
        self.markersize = 7


class Vegetarian(Biotic):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "blue"
        self.markersize = 5

pygame.init()
win=pygame.display.set_mode((field_size*1.1, field_size*1.1))
pygame.display.set_caption('Ecosystem')
game=pygame.Surface((field_size, field_size))

win.fill((150,150,150))

clock=pygame.time.Clock()
pygame.key.set_repeat(200,50)

ecostart()

while play:
    clock.tick(30)

    for e in pygame.event.get():
        if e.type==pygame.QUIT: play=False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE: play=False
            if e.key==pygame.K_SPACE:
                painting = not painting
            if e.key==pygame.K_r: ecostart()
            if e.key==pygame.K_UP and stoper<200: stoper-=2
            if e.key==pygame.K_DOWN and stoper>0: stoper+=2

    if painting:
        drawing()
        pygame.time.delay(int(stoper))

